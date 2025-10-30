#!/usr/bin/env python3
"""
Dynamic Leaderboard Generator
Generates leaderboards from session-specific data
Wrapper around the existing leaderboard system
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import asdict

logger = logging.getLogger(__name__)

# Add leaderboard directory to path
LEADERBOARD_DIR = os.path.join(os.path.dirname(__file__), '..', 'leaderboard')
sys.path.insert(0, LEADERBOARD_DIR)

try:
    from data_loader import DataLoader
    from leaderboard import LeaderboardGenerator
    LEADERBOARD_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import leaderboard modules: {e}")
    LEADERBOARD_AVAILABLE = False


class DynamicLeaderboardGenerator:
    """
    Generates leaderboards from session-specific data files
    Uses the existing leaderboard system with custom paths
    """
    
    def __init__(self):
        """Initialize dynamic leaderboard generator"""
        if not LEADERBOARD_AVAILABLE:
            raise ImportError("Leaderboard modules not available")
    
    def generate_leaderboard(
        self,
        session_dir: str,
        linkedin_weight: float = 0.5,
        github_weight: float = 0.5,
        min_score: float = 0.0,
        top_n: int = 20
    ) -> Dict[str, Any]:
        """
        Generate leaderboard for a session
        
        Args:
            session_dir: Path to session directory
            linkedin_weight: Weight for LinkedIn scores (0-1)
            github_weight: Weight for GitHub scores (0-1)
            min_score: Minimum combined score threshold (0-1)
            top_n: Number of top candidates to return
            
        Returns:
            dict: Leaderboard results with ranked candidates
            
        Raises:
            ValueError: If session directory doesn't exist or data files missing
            FileNotFoundError: If required files not found
        """
        # Validate session directory
        if not os.path.exists(session_dir):
            raise ValueError(f"Session directory not found: {session_dir}")
        
        # Define paths
        linkedin_path = os.path.join(session_dir, 'results.csv')
        github_path = os.path.join(session_dir, 'reports')
        
        # Check if results.csv exists
        if not os.path.exists(linkedin_path):
            logger.warning(f"LinkedIn results not found: {linkedin_path}")
            # Create empty results.csv
            self._create_empty_results_csv(linkedin_path)
        
        # Check if reports directory exists
        if not os.path.exists(github_path):
            logger.warning(f"GitHub reports directory not found: {github_path}")
            os.makedirs(github_path, exist_ok=True)
        
        try:
            # Load data
            logger.info(f"Loading data from session: {session_dir}")
            data_loader = DataLoader(linkedin_path, github_path)
            candidates = data_loader.load_all_data()
            
            if not candidates:
                logger.warning("No candidates found in session data")
                return {
                    'success': True,
                    'leaderboard': [],
                    'total_candidates': 0,
                    'message': 'No candidates found',
                    'weights': {
                        'linkedin': linkedin_weight,
                        'github': github_weight
                    }
                }
            
            logger.info(f"Loaded {len(candidates)} candidates")
            
            # Generate leaderboard
            lb_generator = LeaderboardGenerator(
                candidates,
                linkedin_weight=linkedin_weight,
                github_weight=github_weight,
                min_score=min_score
            )
            
            ranked_candidates = lb_generator.calculate_scores()
            
            # Get top N candidates
            top_candidates = lb_generator.get_top_candidates(top_n)
            
            # Convert to dictionaries for JSON serialization
            leaderboard_data = []
            for candidate in top_candidates:
                candidate_dict = asdict(candidate)
                leaderboard_data.append(candidate_dict)
            
            # Calculate statistics
            all_scores = [c.combined_score for c in ranked_candidates]
            stats = self._calculate_statistics(all_scores)
            
            # Build result
            result = {
                'success': True,
                'leaderboard': leaderboard_data,
                'total_candidates': len(ranked_candidates),
                'top_n': top_n,
                'statistics': stats,
                'weights': {
                    'linkedin': linkedin_weight,
                    'github': github_weight
                },
                'min_score': min_score
            }
            
            # Save leaderboard to session
            self._save_leaderboard_to_session(session_dir, result)
            
            logger.info(f"Generated leaderboard with {len(leaderboard_data)} top candidates")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating leaderboard: {e}", exc_info=True)
            raise
    
    def get_candidate_rank(
        self,
        session_dir: str,
        candidate_name: str,
        linkedin_weight: float = 0.5,
        github_weight: float = 0.5
    ) -> Optional[Dict[str, Any]]:
        """
        Get rank and details for a specific candidate
        
        Args:
            session_dir: Path to session directory
            candidate_name: Name of candidate to find
            linkedin_weight: Weight for LinkedIn scores
            github_weight: Weight for GitHub scores
            
        Returns:
            dict: Candidate details with rank, or None if not found
        """
        try:
            leaderboard = self.generate_leaderboard(
                session_dir,
                linkedin_weight=linkedin_weight,
                github_weight=github_weight,
                top_n=9999  # Get all candidates
            )
            
            # Search for candidate
            for candidate in leaderboard['leaderboard']:
                if candidate['name'].lower() == candidate_name.lower():
                    return candidate
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting candidate rank: {e}")
            return None
    
    def _calculate_statistics(self, scores: List[float]) -> Dict[str, Any]:
        """
        Calculate statistics for leaderboard scores
        
        Args:
            scores: List of combined scores
            
        Returns:
            dict: Statistics (mean, median, min, max)
        """
        if not scores:
            return {
                'mean': 0,
                'median': 0,
                'min': 0,
                'max': 0,
                'count': 0
            }
        
        sorted_scores = sorted(scores)
        n = len(sorted_scores)
        
        # Calculate median
        if n % 2 == 0:
            median = (sorted_scores[n//2 - 1] + sorted_scores[n//2]) / 2
        else:
            median = sorted_scores[n//2]
        
        return {
            'mean': round(sum(scores) / n, 4),
            'median': round(median, 4),
            'min': round(min(scores), 4),
            'max': round(max(scores), 4),
            'count': n
        }
    
    def _save_leaderboard_to_session(
        self,
        session_dir: str,
        leaderboard_data: Dict[str, Any]
    ) -> None:
        """
        Save generated leaderboard to session directory
        
        Args:
            session_dir: Path to session directory
            leaderboard_data: Leaderboard data to save
        """
        try:
            output_path = os.path.join(session_dir, 'leaderboard.json')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(leaderboard_data, f, indent=2)
            logger.info(f"Saved leaderboard to: {output_path}")
        except Exception as e:
            logger.warning(f"Failed to save leaderboard to session: {e}")
    
    def _create_empty_results_csv(self, csv_path: str) -> None:
        """
        Create an empty results.csv file
        
        Args:
            csv_path: Path to create CSV file
        """
        import csv
        try:
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Candidate', 'Score'])
            logger.info(f"Created empty results.csv: {csv_path}")
        except Exception as e:
            logger.error(f"Failed to create empty results.csv: {e}")


# Convenience function
def generate_leaderboard_for_session(
    session_dir: str,
    linkedin_weight: float = 0.5,
    github_weight: float = 0.5,
    min_score: float = 0.0,
    top_n: int = 20
) -> Dict[str, Any]:
    """
    Convenience function to generate leaderboard for a session
    
    Args:
        session_dir: Path to session directory
        linkedin_weight: Weight for LinkedIn scores (0-1)
        github_weight: Weight for GitHub scores (0-1)
        min_score: Minimum combined score threshold (0-1)
        top_n: Number of top candidates to return
        
    Returns:
        dict: Leaderboard results
    """
    generator = DynamicLeaderboardGenerator()
    return generator.generate_leaderboard(
        session_dir,
        linkedin_weight=linkedin_weight,
        github_weight=github_weight,
        min_score=min_score,
        top_n=top_n
    )
