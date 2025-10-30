#!/usr/bin/env python3
"""
Leaderboard Service
Consolidated leaderboard generation and ranking logic
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class LeaderboardService:
    """
    Unified leaderboard generation and ranking service
    """
    
    DEFAULT_WEIGHTS = {
        'linkedin': 0.3,
        'github': 0.4,
        'resume': 0.3
    }
    
    def __init__(self):
        """Initialize Leaderboard Service"""
        pass
    
    def generate_leaderboard(
        self,
        candidates: List[Dict[str, Any]],
        weights: Optional[Dict[str, float]] = None,
        sort_by: str = 'combined_score'
    ) -> Dict[str, Any]:
        """
        Generate ranked leaderboard from candidate scores
        
        Args:
            candidates: List of candidate dicts with score information
            weights: Optional custom weights for score components
            sort_by: Field to sort by (default: 'combined_score')
            
        Returns:
            dict: Leaderboard with ranked candidates
            
        Raises:
            ValueError: If candidates list is empty or invalid
        """
        if not candidates:
            raise ValueError("Candidates list cannot be empty")
        
        # Use provided weights or defaults
        weights = weights or self.DEFAULT_WEIGHTS.copy()
        
        # Normalize weights to sum to 1.0
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        
        # Calculate combined scores
        leaderboard = []
        for candidate in candidates:
            scored_candidate = self._score_candidate(candidate, weights)
            leaderboard.append(scored_candidate)
        
        # Sort by specified field
        leaderboard.sort(key=lambda x: x.get(sort_by, 0), reverse=True)
        
        # Assign ranks
        for idx, candidate in enumerate(leaderboard, 1):
            candidate['rank'] = idx
        
        return {
            'success': True,
            'leaderboard': leaderboard,
            'total_candidates': len(leaderboard),
            'weights': weights,
            'sort_by': sort_by,
            'timestamp': datetime.now().isoformat()
        }
    
    def _score_candidate(
        self,
        candidate: Dict[str, Any],
        weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calculate combined score for a candidate
        
        Args:
            candidate: Candidate data dict
            weights: Score component weights
            
        Returns:
            dict: Candidate with calculated combined score
        """
        # Extract scores with defaults
        linkedin_score = float(candidate.get('linkedin_score', 0))
        github_score = float(candidate.get('github_score', 0))
        resume_score = float(candidate.get('resume_score', 0))
        
        # Calculate weighted combined score
        combined_score = (
            linkedin_score * weights.get('linkedin', 0) +
            github_score * weights.get('github', 0) +
            resume_score * weights.get('resume', 0)
        )
        
        return {
            'name': candidate.get('name', 'Unknown'),
            'linkedin_score': round(linkedin_score, 2),
            'github_score': round(github_score, 2),
            'resume_score': round(resume_score, 2),
            'combined_score': round(combined_score, 2),
            'github_username': candidate.get('github_username', ''),
            'linkedin_url': candidate.get('linkedin_url', ''),
            'email': candidate.get('email', ''),
            'rank': 0  # Will be set after sorting
        }
    
    def filter_leaderboard(
        self,
        leaderboard: List[Dict[str, Any]],
        min_score: Optional[float] = None,
        max_rank: Optional[int] = None,
        required_skills: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter leaderboard based on criteria
        
        Args:
            leaderboard: List of ranked candidates
            min_score: Minimum combined score threshold
            max_rank: Maximum rank to include
            required_skills: List of required skills (if available in candidate data)
            
        Returns:
            list: Filtered leaderboard
        """
        filtered = leaderboard.copy()
        
        # Filter by minimum score
        if min_score is not None:
            filtered = [c for c in filtered if c.get('combined_score', 0) >= min_score]
        
        # Filter by maximum rank
        if max_rank is not None:
            filtered = [c for c in filtered if c.get('rank', float('inf')) <= max_rank]
        
        # Filter by required skills (if skill data available)
        if required_skills:
            filtered = [
                c for c in filtered
                if self._has_required_skills(c, required_skills)
            ]
        
        return filtered
    
    def _has_required_skills(
        self,
        candidate: Dict[str, Any],
        required_skills: List[str]
    ) -> bool:
        """
        Check if candidate has required skills
        
        Args:
            candidate: Candidate data
            required_skills: List of required skills
            
        Returns:
            bool: True if candidate has all required skills
        """
        candidate_skills = candidate.get('skills', [])
        if isinstance(candidate_skills, str):
            candidate_skills = [s.strip().lower() for s in candidate_skills.split(',')]
        else:
            candidate_skills = [s.lower() for s in candidate_skills]
        
        required_lower = [s.lower() for s in required_skills]
        
        return all(skill in candidate_skills for skill in required_lower)
    
    def get_top_candidates(
        self,
        leaderboard: List[Dict[str, Any]],
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top N candidates from leaderboard
        
        Args:
            leaderboard: List of ranked candidates
            count: Number of top candidates to return
            
        Returns:
            list: Top N candidates
        """
        return leaderboard[:count]
    
    def compare_candidates(
        self,
        candidate1: Dict[str, Any],
        candidate2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare two candidates
        
        Args:
            candidate1: First candidate data
            candidate2: Second candidate data
            
        Returns:
            dict: Comparison results
        """
        c1_score = candidate1.get('combined_score', 0)
        c2_score = candidate2.get('combined_score', 0)
        
        return {
            'candidate1': {
                'name': candidate1.get('name'),
                'combined_score': c1_score,
                'github_score': candidate1.get('github_score', 0),
                'linkedin_score': candidate1.get('linkedin_score', 0),
                'resume_score': candidate1.get('resume_score', 0)
            },
            'candidate2': {
                'name': candidate2.get('name'),
                'combined_score': c2_score,
                'github_score': candidate2.get('github_score', 0),
                'linkedin_score': candidate2.get('linkedin_score', 0),
                'resume_score': candidate2.get('resume_score', 0)
            },
            'score_difference': abs(c1_score - c2_score),
            'winner': candidate1.get('name') if c1_score > c2_score else candidate2.get('name'),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_statistics(
        self,
        leaderboard: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate statistics for leaderboard
        
        Args:
            leaderboard: List of ranked candidates
            
        Returns:
            dict: Statistical summary
        """
        if not leaderboard:
            return {
                'count': 0,
                'avg_score': 0,
                'max_score': 0,
                'min_score': 0
            }
        
        scores = [c.get('combined_score', 0) for c in leaderboard]
        
        return {
            'count': len(leaderboard),
            'avg_score': round(sum(scores) / len(scores), 2),
            'max_score': round(max(scores), 2),
            'min_score': round(min(scores), 2),
            'median_score': round(sorted(scores)[len(scores) // 2], 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Check if leaderboard service is available
        
        Returns:
            dict: Service status information
        """
        return {
            'service': 'leaderboard',
            'available': True,
            'default_weights': self.DEFAULT_WEIGHTS
        }


def create_leaderboard_service() -> LeaderboardService:
    """
    Factory function to create Leaderboard service instance
    
    Returns:
        LeaderboardService instance
    """
    return LeaderboardService()
