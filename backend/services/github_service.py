#!/usr/bin/env python3
"""
GitHub Service
Consolidated GitHub profile analysis service with improved error handling
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add github-data-fetch to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'github-data-fetch'))

try:
    from data_fetcher import GitHubDataFetcher
    from analyzer import GitHubAnalyzer
    from matcher import CandidateMatcher
except ImportError as e:
    logging.error(f"Failed to import GitHub modules: {e}")
    GitHubDataFetcher = None
    GitHubAnalyzer = None
    CandidateMatcher = None

logger = logging.getLogger(__name__)


class GitHubService:
    """
    Unified GitHub profile analysis service
    """
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize GitHub service
        
        Args:
            github_token: GitHub Personal Access Token (defaults to GITHUB_TOKEN env var)
        """
        self.token = github_token or os.environ.get('GITHUB_TOKEN')
        
        if not all([GitHubDataFetcher, GitHubAnalyzer, CandidateMatcher]):
            raise ImportError(
                "GitHub analysis modules not available. "
                "Please ensure github-data-fetch dependencies are installed."
            )
        
        # GitHubDataFetcher expects 'access_token' parameter, not 'token'
        self.fetcher = GitHubDataFetcher(access_token=self.token)
        # Don't initialize analyzer here - it needs data which we get per-request
        self.analyzer_class = GitHubAnalyzer
    
    def validate_username(self, username: str) -> tuple[bool, Optional[str]]:
        """
        Validate GitHub username format
        
        Args:
            username: GitHub username to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not username:
            return False, "Username cannot be empty"
        
        if len(username) > 39:
            return False, "Username too long (max 39 characters)"
        
        # Basic validation - alphanumeric and hyphens
        if not all(c.isalnum() or c == '-' for c in username):
            return False, "Username contains invalid characters"
        
        if username.startswith('-') or username.endswith('-'):
            return False, "Username cannot start or end with a hyphen"
        
        return True, None
    
    def analyze_profile(
        self,
        username: str,
        job_requirements: Optional[Dict[str, Any]] = None,
        max_repos: int = 20
    ) -> Dict[str, Any]:
        """
        Analyze a GitHub profile
        
        Args:
            username: GitHub username
            job_requirements: Optional job requirements for matching
            max_repos: Maximum number of repositories to analyze
            
        Returns:
            dict: Analysis results including profile data, analysis, and optional match score
            
        Raises:
            ValueError: If username is invalid
            RuntimeError: If GitHub API fails
        """
        # Validate username
        is_valid, error_msg = self.validate_username(username)
        if not is_valid:
            raise ValueError(f"Invalid username: {error_msg}")
        
        try:
            # Fetch user profile
            logger.info(f"Fetching GitHub profile for: {username}")
            user_data = self.fetcher.fetch_user_profile(username)
            
            if not user_data:
                raise RuntimeError(f"Failed to fetch GitHub profile for {username}")
            
            # Fetch repositories
            logger.info(f"Fetching repositories for: {username}")
            repos = self.fetcher.fetch_repositories(limit=max_repos)
            
            # Prepare data structure for analyzer
            analysis_data = {
                'profile': user_data,
                'all_repositories': repos,
                'top_repositories': repos[:max_repos]
            }
            
            # Analyze profile - GitHubAnalyzer expects data dict in constructor
            logger.info(f"Analyzing profile for: {username}")
            analyzer = self.analyzer_class(analysis_data)
            analysis = analyzer.perform_complete_analysis()
            
            result = {
                'success': True,
                'username': username,
                'profile': {
                    'name': user_data.get('name'),
                    'bio': user_data.get('bio'),
                    'location': user_data.get('location'),
                    'company': user_data.get('company'),
                    'followers': user_data.get('followers'),
                    'public_repos': user_data.get('public_repos'),
                    'created_at': user_data.get('created_at'),
                },
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }
            
            # Calculate match score if job requirements provided
            if job_requirements:
                logger.info(f"Calculating match score for: {username}")
                matcher = CandidateMatcher(job_requirements)
                match_result = matcher.calculate_match_score(analysis)
                result['match_score'] = match_result.get('overall_score', 0)
                result['match_details'] = match_result
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing GitHub profile {username}: {e}")
            raise RuntimeError(f"GitHub analysis failed: {str(e)}")
    
    def batch_analyze(
        self,
        usernames: List[str],
        job_requirements: Optional[Dict[str, Any]] = None,
        max_repos: int = 10
    ) -> Dict[str, Any]:
        """
        Analyze multiple GitHub profiles
        
        Args:
            usernames: List of GitHub usernames
            job_requirements: Optional job requirements for matching
            max_repos: Maximum number of repositories to analyze per user
            
        Returns:
            dict: Batch analysis results with success/failure for each username
        """
        results = []
        errors = []
        
        for username in usernames:
            try:
                result = self.analyze_profile(username, job_requirements, max_repos)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to analyze {username}: {e}")
                errors.append({
                    'username': username,
                    'error': str(e)
                })
        
        return {
            'success': True,
            'total': len(usernames),
            'successful': len(results),
            'failed': len(errors),
            'results': results,
            'errors': errors,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Check if GitHub service is available
        
        Returns:
            dict: Service status information
        """
        return {
            'service': 'github',
            'available': all([GitHubDataFetcher, GitHubAnalyzer, CandidateMatcher]),
            'has_token': bool(self.token),
            'modules_loaded': {
                'data_fetcher': GitHubDataFetcher is not None,
                'analyzer': GitHubAnalyzer is not None,
                'matcher': CandidateMatcher is not None
            }
        }


def create_github_service(token: Optional[str] = None) -> GitHubService:
    """
    Factory function to create GitHub service instance
    
    Args:
        token: Optional GitHub token
        
    Returns:
        GitHubService instance
    """
    try:
        return GitHubService(token)
    except ImportError as e:
        logger.error(f"Cannot create GitHub service: {e}")
        raise
