#!/usr/bin/env python3
"""
GitHub Analysis Generator
Extracts GitHub usernames from resumes and generates analysis JSON files
Compatible with the leaderboard system's expected format
"""

import os
import json
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class GitHubAnalysisGenerator:
    """
    Generates GitHub analysis JSON files for candidates
    Compatible with leaderboard system's analysis_*.json format
    """
    
    def __init__(self, github_service=None):
        """
        Initialize GitHub Analysis Generator
        
        Args:
            github_service: Optional GitHubService instance (will be imported if not provided)
        """
        self.github_service = github_service
        
        # Import github_service if not provided
        if not self.github_service:
            try:
                import sys
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services'))
                from github_service import create_github_service
                self.github_service = create_github_service()
                logger.info("GitHub service initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize GitHub service: {e}")
                self.github_service = None
    
    def extract_github_username(self, resume_text: str) -> Optional[str]:
        """
        Extract GitHub username from resume text
        
        Patterns matched:
        - github.com/username
        - @username (GitHub context)
        - Full GitHub URLs
        
        Args:
            resume_text: Full text content of resume
            
        Returns:
            str: GitHub username or None if not found
        """
        if not resume_text:
            return None
        
        # Pattern 1: github.com/username
        pattern1 = r'github\.com/([a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38})'
        match = re.search(pattern1, resume_text, re.IGNORECASE)
        if match:
            username = match.group(1)
            # Filter out common false positives
            if username.lower() not in ['features', 'pricing', 'about', 'login', 'signup']:
                return username
        
        # Pattern 2: GitHub: username or GitHub - username
        pattern2 = r'GitHub\s*[:\-]\s*@?([a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38})'
        match = re.search(pattern2, resume_text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Pattern 3: @username in GitHub context
        pattern3 = r'(?:GitHub|Git)\s+@([a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38})'
        match = re.search(pattern3, resume_text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return None
    
    def analyze_github_profile(
        self,
        username: str,
        job_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a GitHub profile using the GitHub service
        
        Args:
            username: GitHub username
            job_requirements: Optional job requirements for matching
            
        Returns:
            dict: Analysis results compatible with leaderboard format
        """
        if not self.github_service:
            logger.warning("GitHub service not available")
            return self._create_minimal_analysis(username, error="GitHub service not available")
        
        try:
            # Analyze profile using GitHub service
            result = self.github_service.analyze_profile(
                username,
                job_requirements=job_requirements,
                max_repos=20
            )
            
            if not result.get('success'):
                logger.warning(f"GitHub analysis failed for {username}: {result.get('error')}")
                return self._create_minimal_analysis(username, error=result.get('error'))
            
            # Transform to leaderboard-compatible format
            analysis = self._transform_to_leaderboard_format(username, result)
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing GitHub profile {username}: {e}")
            return self._create_minimal_analysis(username, error=str(e))
    
    def _transform_to_leaderboard_format(
        self,
        username: str,
        service_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transform GitHub service result to leaderboard-compatible format
        
        Args:
            username: GitHub username
            service_result: Result from GitHub service
            
        Returns:
            dict: Transformed analysis in leaderboard format
        """
        # Extract relevant data
        profile = service_result.get('profile', {})
        analysis = service_result.get('analysis', {})
        
        # Calculate overall score (0-100 scale as expected by leaderboard)
        overall_score = analysis.get('overall_score', 0.0)
        if isinstance(overall_score, float) and overall_score <= 1.0:
            overall_score = overall_score * 100  # Convert 0-1 to 0-100
        
        # Build leaderboard-compatible structure
        leaderboard_format = {
            'username': username,
            'analysis_date': datetime.now().isoformat(),
            'profile': {
                'name': profile.get('name'),
                'bio': profile.get('bio'),
                'location': profile.get('location'),
                'company': profile.get('company'),
                'followers': profile.get('followers', 0),
                'public_repos': profile.get('public_repos', 0),
                'created_at': profile.get('created_at')
            },
            'metrics': {
                'overall_score': round(overall_score, 2),
                'total_repos': analysis.get('total_repos', 0),
                'total_stars': analysis.get('total_stars', 0),
                'total_commits': analysis.get('total_commits', 0),
                'languages': analysis.get('languages', {}),
                'activity_score': analysis.get('activity_score', 0),
                'quality_score': analysis.get('quality_score', 0),
                'popularity_score': analysis.get('popularity_score', 0)
            },
            'top_repositories': service_result.get('top_repositories', [])[:5],
            'skills_matched': analysis.get('skills_matched', []),
            'compatibility': analysis.get('compatibility_score', 0)
        }
        
        return leaderboard_format
    
    def _create_minimal_analysis(
        self,
        username: str,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create minimal analysis structure when full analysis fails
        
        Args:
            username: GitHub username
            error: Error message (optional)
            
        Returns:
            dict: Minimal analysis structure
        """
        return {
            'username': username,
            'analysis_date': datetime.now().isoformat(),
            'error': error,
            'profile': {},
            'metrics': {
                'overall_score': 0,
                'total_repos': 0,
                'total_stars': 0,
                'total_commits': 0,
                'languages': {},
                'activity_score': 0,
                'quality_score': 0,
                'popularity_score': 0
            },
            'top_repositories': [],
            'skills_matched': [],
            'compatibility': 0
        }
    
    def generate_analyses_for_candidates(
        self,
        candidates: List[Dict[str, Any]],
        job_requirements: Optional[Dict[str, Any]],
        session_dir: str,
        skip_on_error: bool = True
    ) -> Dict[str, Any]:
        """
        Generate GitHub analyses for all candidates and save JSON files
        
        Args:
            candidates: List of candidate dictionaries with 'name' and 'text'
            job_requirements: Optional job requirements for matching
            session_dir: Session directory to save analysis files
            skip_on_error: If True, skip candidates with errors instead of failing
            
        Returns:
            dict: Summary of generated analyses
        """
        reports_dir = os.path.join(session_dir, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        logger.info(f"Generating GitHub analyses for {len(candidates)} candidates")
        
        analyses_generated = 0
        analyses_failed = 0
        analyses_skipped = 0
        
        results = []
        
        for candidate in candidates:
            name = candidate.get('name', 'Unknown')
            resume_text = candidate.get('text', '')
            
            # Extract GitHub username
            github_username = self.extract_github_username(resume_text)
            
            if not github_username:
                logger.info(f"No GitHub username found for candidate: {name}")
                analyses_skipped += 1
                results.append({
                    'candidate': name,
                    'status': 'skipped',
                    'reason': 'No GitHub username found'
                })
                continue
            
            logger.info(f"Found GitHub username for {name}: {github_username}")
            
            try:
                # Analyze GitHub profile
                analysis = self.analyze_github_profile(github_username, job_requirements)
                
                # Save to JSON file
                json_filename = f"analysis_{github_username}.json"
                json_path = os.path.join(reports_dir, json_filename)
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(analysis, f, indent=2)
                
                logger.info(f"✅ Saved analysis for {github_username} to {json_filename}")
                
                analyses_generated += 1
                results.append({
                    'candidate': name,
                    'github_username': github_username,
                    'status': 'success',
                    'file': json_filename,
                    'score': analysis['metrics']['overall_score']
                })
                
            except Exception as e:
                logger.error(f"Failed to generate analysis for {name} ({github_username}): {e}")
                analyses_failed += 1
                
                if not skip_on_error:
                    raise
                
                results.append({
                    'candidate': name,
                    'github_username': github_username,
                    'status': 'failed',
                    'error': str(e)
                })
        
        summary = {
            'success': True,
            'reports_dir': reports_dir,
            'total_candidates': len(candidates),
            'analyses_generated': analyses_generated,
            'analyses_failed': analyses_failed,
            'analyses_skipped': analyses_skipped,
            'results': results
        }
        
        logger.info(f"GitHub analysis summary: {analyses_generated} generated, "
                   f"{analyses_failed} failed, {analyses_skipped} skipped")
        
        return summary


# Convenience functions
def create_github_analysis_generator(github_service=None) -> GitHubAnalysisGenerator:
    """
    Create a GitHubAnalysisGenerator instance
    
    Args:
        github_service: Optional GitHub service instance
        
    Returns:
        GitHubAnalysisGenerator: Configured generator
    """
    return GitHubAnalysisGenerator(github_service)


def generate_github_analyses(
    candidates: List[Dict[str, Any]],
    job_requirements: Optional[Dict[str, Any]],
    session_dir: str,
    github_service=None
) -> Dict[str, Any]:
    """
    Convenience function to generate GitHub analyses
    
    Args:
        candidates: List of candidates with name and text
        job_requirements: Optional job requirements
        session_dir: Session directory for output
        github_service: Optional GitHub service instance
        
    Returns:
        dict: Summary of generated analyses
    """
    generator = create_github_analysis_generator(github_service)
    return generator.generate_analyses_for_candidates(
        candidates,
        job_requirements,
        session_dir
    )
