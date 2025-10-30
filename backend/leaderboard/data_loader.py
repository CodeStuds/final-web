"""
Data loader module for LinkedIn and GitHub candidate scores
"""

import os
import csv
import json
import glob
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from utils import normalize_github_score, normalize_linkedin_score, normalize_name
from config import LINKEDIN_DATA_PATH, GITHUB_DATA_PATH


@dataclass
class CandidateScore:
    """Data class for candidate scores"""
    name: str
    linkedin_score: Optional[float] = None
    github_score: Optional[float] = None
    github_username: Optional[str] = None
    linkedin_raw_score: Optional[float] = None
    github_raw_score: Optional[float] = None


class DataLoader:
    """Loads and parses candidate data from multiple sources"""
    
    def __init__(
        self,
        linkedin_path: str = None,
        github_path: str = None
    ):
        """
        Initialize data loader
        
        Args:
            linkedin_path: Path to LinkedIn results CSV
            github_path: Path to GitHub reports directory
        """
        self.linkedin_path = linkedin_path or LINKEDIN_DATA_PATH
        self.github_path = github_path or GITHUB_DATA_PATH
        
        self.candidates: Dict[str, CandidateScore] = {}
    
    def load_linkedin_scores(self) -> Dict[str, float]:
        """
        Load scores from LinkedIn data (ibhanwork results.csv)
        
        Returns:
            Dictionary mapping candidate name to score (0-1)
        """
        scores = {}
        
        if not os.path.exists(self.linkedin_path):
            print(f"⚠️  LinkedIn data not found at: {self.linkedin_path}")
            return scores
        
        try:
            with open(self.linkedin_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # CSV should have 'Candidate' and 'Score' columns
                    candidate = row.get('Candidate', '').strip()
                    score_str = row.get('Score', '0')
                    
                    if candidate:
                        try:
                            score = float(score_str)
                            normalized_score = normalize_linkedin_score(score)
                            scores[candidate] = normalized_score
                        except ValueError:
                            print(f"⚠️  Invalid score for {candidate}: {score_str}")
                            continue
            
            print(f"✅ Loaded {len(scores)} LinkedIn scores")
            
        except Exception as e:
            print(f"❌ Error loading LinkedIn data: {e}")
        
        return scores
    
    def load_github_scores(self) -> Dict[str, Dict[str, Any]]:
        """
        Load scores from GitHub analysis JSON files
        
        Returns:
            Dictionary mapping GitHub username to score data
        """
        scores = {}
        
        if not os.path.exists(self.github_path):
            print(f"⚠️  GitHub data directory not found at: {self.github_path}")
            return scores
        
        # Find all analysis JSON files
        json_pattern = os.path.join(self.github_path, "analysis_*.json")
        json_files = glob.glob(json_pattern)
        
        if not json_files:
            print(f"⚠️  No GitHub analysis files found in: {self.github_path}")
            return scores
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract username from filename (analysis_USERNAME.json)
                filename = os.path.basename(json_file)
                username = filename.replace('analysis_', '').replace('.json', '')
                
                # Get match score
                match_data = data.get('match_results', {})
                overall_score = match_data.get('overall_score', 0)
                
                # Get profile info
                profile = data.get('analysis', {}).get('profile', {})
                name = profile.get('name') or username
                
                # Normalize score to 0-1
                normalized_score = normalize_github_score(overall_score)
                
                scores[username] = {
                    'name': name,
                    'score': normalized_score,
                    'raw_score': overall_score,
                    'username': username
                }
                
            except Exception as e:
                print(f"⚠️  Error loading {json_file}: {e}")
                continue
        
        print(f"✅ Loaded {len(scores)} GitHub scores")
        
        return scores
    
    def merge_candidate_data(
        self,
        linkedin_scores: Dict[str, float],
        github_scores: Dict[str, Dict[str, Any]]
    ) -> Dict[str, CandidateScore]:
        """
        Merge LinkedIn and GitHub data by matching candidate names
        
        Args:
            linkedin_scores: LinkedIn scores by name
            github_scores: GitHub scores by username
        
        Returns:
            Dictionary of merged candidate scores
        """
        candidates = {}
        
        # First, add all GitHub candidates
        for username, github_data in github_scores.items():
            normalized_name = normalize_name(github_data['name'])
            
            candidates[normalized_name] = CandidateScore(
                name=github_data['name'],
                github_score=github_data['score'],
                github_raw_score=github_data['raw_score'],
                github_username=username
            )
        
        # Then, match LinkedIn candidates
        for linkedin_name, linkedin_score in linkedin_scores.items():
            normalized_name = normalize_name(linkedin_name)
            
            if normalized_name in candidates:
                # Match found - update existing candidate
                candidates[normalized_name].linkedin_score = linkedin_score
                candidates[normalized_name].linkedin_raw_score = linkedin_score
            else:
                # New candidate from LinkedIn only
                candidates[normalized_name] = CandidateScore(
                    name=linkedin_name,
                    linkedin_score=linkedin_score,
                    linkedin_raw_score=linkedin_score
                )
        
        return candidates
    
    def load_all_data(self) -> Dict[str, CandidateScore]:
        """
        Load and merge all candidate data
        
        Returns:
            Dictionary of all candidates with their scores
        """
        print("\n📊 Loading candidate data...")
        print("=" * 60)
        
        # Load from both sources
        linkedin_scores = self.load_linkedin_scores()
        github_scores = self.load_github_scores()
        
        # Merge data
        self.candidates = self.merge_candidate_data(linkedin_scores, github_scores)
        
        # Statistics
        total = len(self.candidates)
        both_scores = sum(1 for c in self.candidates.values() 
                         if c.linkedin_score is not None and c.github_score is not None)
        linkedin_only = sum(1 for c in self.candidates.values() 
                           if c.linkedin_score is not None and c.github_score is None)
        github_only = sum(1 for c in self.candidates.values() 
                         if c.linkedin_score is None and c.github_score is not None)
        
        print(f"\n📈 Data Summary:")
        print(f"   Total candidates: {total}")
        print(f"   Both scores: {both_scores}")
        print(f"   LinkedIn only: {linkedin_only}")
        print(f"   GitHub only: {github_only}")
        print("=" * 60)
        
        return self.candidates
