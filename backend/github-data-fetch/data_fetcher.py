"""
Data Fetcher Module for HireSight
Handles all GitHub API interactions using PyGithub
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from github import Github, GithubException, RateLimitExceededException
import json
import base64
import yaml
import toml
from xml.etree import ElementTree as ET

from utils import logger, retry_on_rate_limit, handle_api_error, calculate_months_ago
from config import PACKAGE_FILES, CICD_FILES


class GitHubDataFetcher:
    """Fetches comprehensive data from GitHub API"""
    
    def __init__(self, access_token: Optional[str] = None):
        """Initialize GitHub API client"""
        self.access_token = access_token or os.getenv('GITHUB_TOKEN')
        
        if not self.access_token:
            logger.warning("No GitHub token provided. API rate limits will be restrictive.")
            self.github = Github()
        else:
            self.github = Github(self.access_token)
        
        self.user = None
        self.repos = []
    
    def check_rate_limit(self) -> Dict[str, int]:
        """Check current API rate limit status"""
        try:
            rate_limit = self.github.get_rate_limit()
            # Handle different PyGithub versions
            if hasattr(rate_limit, 'core'):
                core = rate_limit.core
            else:
                # Newer versions use direct attributes
                core = rate_limit
            
            return {
                'core_remaining': core.remaining if hasattr(core, 'remaining') else 5000,
                'core_limit': core.limit if hasattr(core, 'limit') else 5000,
                'core_reset': core.reset.isoformat() if hasattr(core, 'reset') and core.reset else None
            }
        except Exception as e:
            logger.warning(f"Could not check rate limit: {e}")
            return {'core_remaining': 5000, 'core_limit': 5000, 'core_reset': None}
    
    @retry_on_rate_limit(max_retries=3)
    def fetch_user_profile(self, username: str) -> Dict[str, Any]:
        """
        Fetch basic user profile information
        Returns: Profile metadata
        """
        try:
            logger.info(f"Fetching profile for user: {username}")
            self.user = self.github.get_user(username)
            
            # Calculate account age
            created_at = self.user.created_at
            account_age_months = calculate_months_ago(created_at)
            
            profile_data = {
                'username': self.user.login,
                'name': self.user.name,
                'bio': self.user.bio,
                'location': self.user.location,
                'email': self.user.email,
                'company': self.user.company,
                'blog': self.user.blog,
                'twitter_username': self.user.twitter_username,
                'public_repos': self.user.public_repos,
                'public_gists': self.user.public_gists,
                'followers': self.user.followers,
                'following': self.user.following,
                'created_at': created_at.isoformat(),
                'updated_at': self.user.updated_at.isoformat() if self.user.updated_at else None,
                'account_age_months': account_age_months,
                'hireable': self.user.hireable,
            }
            
            logger.info(f"Profile fetched successfully for {username}")
            return profile_data
            
        except GithubException as e:
            logger.error(f"GitHub API error fetching profile: {e}")
            raise Exception(f"Failed to fetch profile for {username}: {e.data.get('message', str(e))}")
    
    @retry_on_rate_limit(max_retries=3)
    def fetch_repositories(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch user's repositories with metadata
        Returns: List of repository data
        """
        if not self.user:
            raise Exception("User profile not loaded. Call fetch_user_profile first.")
        
        try:
            logger.info(f"Fetching repositories for {self.user.login}")
            repos_data = []
            
            # Get all public repos
            repos = self.user.get_repos(type='owner', sort='updated', direction='desc')
            
            count = 0
            for repo in repos:
                if count >= limit:
                    break
                
                # Skip forks optionally (we'll include them but mark them)
                repo_info = {
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'description': repo.description,
                    'url': repo.html_url,
                    'is_fork': repo.fork,
                    'is_private': repo.private,
                    'created_at': repo.created_at.isoformat(),
                    'updated_at': repo.updated_at.isoformat(),
                    'pushed_at': repo.pushed_at.isoformat() if repo.pushed_at else None,
                    'size': repo.size,  # KB
                    'stargazers_count': repo.stargazers_count,
                    'watchers_count': repo.watchers_count,
                    'forks_count': repo.forks_count,
                    'open_issues_count': repo.open_issues_count,
                    'language': repo.language,
                    'languages': {},  # Will fetch separately
                    'topics': repo.get_topics(),
                    'has_issues': repo.has_issues,
                    'has_projects': repo.has_projects,
                    'has_wiki': repo.has_wiki,
                    'has_downloads': repo.has_downloads,
                    'license': repo.license.name if repo.license else None,
                    'default_branch': repo.default_branch,
                }
                
                # Fetch language breakdown
                try:
                    languages = repo.get_languages()
                    repo_info['languages'] = languages
                except:
                    logger.debug(f"Could not fetch languages for {repo.name}")
                
                repos_data.append(repo_info)
                self.repos.append(repo)  # Keep repo object for later use
                count += 1
            
            logger.info(f"Fetched {len(repos_data)} repositories")
            return repos_data
            
        except GithubException as e:
            logger.error(f"Error fetching repositories: {e}")
            return []
    
    def get_top_active_repos(self, repos_data: List[Dict], count: int = 10) -> List[Dict]:
        """
        Get top N most active repositories based on recent activity and stars
        """
        # Score repos based on recency and popularity
        scored_repos = []
        for repo in repos_data:
            if repo['is_fork']:
                continue  # Skip forks for deep analysis
            
            # Calculate activity score
            if repo['pushed_at']:
                pushed_date = datetime.fromisoformat(repo['pushed_at'].replace('Z', '+00:00'))
                months_ago = calculate_months_ago(pushed_date)
                recency_score = max(0, 12 - months_ago)  # 0-12 score
            else:
                recency_score = 0
            
            popularity_score = (
                repo['stargazers_count'] * 3 +
                repo['forks_count'] * 2 +
                repo['watchers_count']
            ) / 10  # Normalize
            
            total_score = recency_score * 2 + popularity_score
            scored_repos.append((total_score, repo))
        
        # Sort by score and return top N
        scored_repos.sort(reverse=True, key=lambda x: x[0])
        top_repos = [repo for score, repo in scored_repos[:count]]
        
        logger.info(f"Selected top {len(top_repos)} active repositories")
        return top_repos
    
    @retry_on_rate_limit(max_retries=2)
    def fetch_repository_files(self, repo_full_name: str, file_patterns: List[str]) -> Dict[str, str]:
        """
        Fetch specific files from repository (e.g., package.json, requirements.txt)
        Returns: Dict of filename -> content
        """
        files_content = {}
        
        try:
            repo = self.github.get_repo(repo_full_name)
            
            for file_path in file_patterns:
                try:
                    file_content = repo.get_contents(file_path)
                    
                    if isinstance(file_content, list):
                        continue  # Skip directories
                    
                    # Decode content
                    content = base64.b64decode(file_content.content).decode('utf-8')
                    files_content[file_path] = content
                    logger.debug(f"Fetched {file_path} from {repo_full_name}")
                    
                except GithubException as e:
                    if e.status == 404:
                        continue  # File not found
                    logger.debug(f"Could not fetch {file_path}: {e}")
                except Exception as e:
                    logger.debug(f"Error decoding {file_path}: {e}")
            
        except Exception as e:
            logger.error(f"Error fetching files from {repo_full_name}: {e}")
        
        return files_content
    
    @retry_on_rate_limit(max_retries=2)
    def fetch_commits(self, repo_full_name: str, since_date: Optional[datetime] = None, max_commits: int = 200) -> List[Dict[str, Any]]:
        """
        Fetch commits from repository
        Returns: List of commit data
        """
        if since_date is None:
            # Default to last 12 months
            since_date = datetime.now() - timedelta(days=365)
        
        commits_data = []
        
        try:
            repo = self.github.get_repo(repo_full_name)
            commits = repo.get_commits(since=since_date, author=self.user)
            
            count = 0
            for commit in commits:
                if count >= max_commits:
                    break
                
                commit_info = {
                    'sha': commit.sha,
                    'message': commit.commit.message,
                    'author': commit.commit.author.name if commit.commit.author else None,
                    'date': commit.commit.author.date.isoformat() if commit.commit.author else None,
                    'additions': commit.stats.additions if commit.stats else 0,
                    'deletions': commit.stats.deletions if commit.stats else 0,
                    'total_changes': commit.stats.total if commit.stats else 0,
                }
                
                commits_data.append(commit_info)
                count += 1
            
            logger.debug(f"Fetched {len(commits_data)} commits from {repo_full_name}")
            
        except GithubException as e:
            logger.debug(f"Error fetching commits from {repo_full_name}: {e}")
        
        return commits_data
    
    @retry_on_rate_limit(max_retries=2)
    def fetch_pull_requests(self, repo_full_name: str, state: str = 'all', max_prs: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch pull requests from repository
        Returns: List of PR data
        """
        prs_data = []
        
        try:
            repo = self.github.get_repo(repo_full_name)
            pulls = repo.get_pulls(state=state, sort='created', direction='desc')
            
            count = 0
            for pr in pulls:
                if count >= max_prs:
                    break
                
                # Only include PRs by the user
                if pr.user.login != self.user.login:
                    continue
                
                pr_info = {
                    'number': pr.number,
                    'title': pr.title,
                    'state': pr.state,
                    'created_at': pr.created_at.isoformat(),
                    'updated_at': pr.updated_at.isoformat() if pr.updated_at else None,
                    'closed_at': pr.closed_at.isoformat() if pr.closed_at else None,
                    'merged_at': pr.merged_at.isoformat() if pr.merged_at else None,
                    'merged': pr.merged,
                    'comments_count': pr.comments,
                    'review_comments_count': pr.review_comments,
                    'commits_count': pr.commits,
                    'additions': pr.additions,
                    'deletions': pr.deletions,
                    'changed_files': pr.changed_files,
                }
                
                prs_data.append(pr_info)
                count += 1
            
            logger.debug(f"Fetched {len(prs_data)} pull requests from {repo_full_name}")
            
        except GithubException as e:
            logger.debug(f"Error fetching PRs from {repo_full_name}: {e}")
        
        return prs_data
    
    @retry_on_rate_limit(max_retries=2)
    def fetch_reviews_given(self, repo_full_name: str, max_reviews: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch code reviews given by the user
        Returns: List of review data
        """
        reviews_data = []
        
        try:
            repo = self.github.get_repo(repo_full_name)
            pulls = repo.get_pulls(state='all', sort='created', direction='desc')
            
            review_count = 0
            for pr in pulls:
                if review_count >= max_reviews:
                    break
                
                try:
                    reviews = pr.get_reviews()
                    for review in reviews:
                        if review_count >= max_reviews:
                            break
                        
                        # Only include reviews by the user
                        if review.user.login != self.user.login:
                            continue
                        
                        review_info = {
                            'pr_number': pr.number,
                            'pr_title': pr.title,
                            'state': review.state,
                            'body': review.body or '',
                            'submitted_at': review.submitted_at.isoformat() if review.submitted_at else None,
                        }
                        
                        reviews_data.append(review_info)
                        review_count += 1
                        
                except Exception as e:
                    logger.debug(f"Error fetching reviews for PR #{pr.number}: {e}")
            
            logger.debug(f"Fetched {len(reviews_data)} code reviews from {repo_full_name}")
            
        except GithubException as e:
            logger.debug(f"Error fetching reviews from {repo_full_name}: {e}")
        
        return reviews_data
    
    def check_cicd_presence(self, repo_full_name: str) -> Dict[str, bool]:
        """
        Check for CI/CD configuration files in repository
        Returns: Dict of CI/CD tools found
        """
        cicd_found = {}
        
        try:
            repo = self.github.get_repo(repo_full_name)
            
            # Check for GitHub Actions
            try:
                workflows = repo.get_contents('.github/workflows')
                cicd_found['github_actions'] = True
            except:
                cicd_found['github_actions'] = False
            
            # Check for other CI/CD files
            cicd_files = [
                ('.gitlab-ci.yml', 'gitlab_ci'),
                ('.travis.yml', 'travis_ci'),
                ('Jenkinsfile', 'jenkins'),
                ('.circleci/config.yml', 'circleci'),
                ('azure-pipelines.yml', 'azure_pipelines'),
            ]
            
            for file_path, tool_name in cicd_files:
                try:
                    repo.get_contents(file_path)
                    cicd_found[tool_name] = True
                except:
                    cicd_found[tool_name] = False
            
        except Exception as e:
            logger.debug(f"Error checking CI/CD for {repo_full_name}: {e}")
        
        return cicd_found
    
    def parse_package_file(self, filename: str, content: str) -> List[str]:
        """
        Parse package/dependency file and extract dependencies
        Returns: List of dependency names
        """
        dependencies = []
        
        try:
            if filename == 'package.json':
                data = json.loads(content)
                deps = data.get('dependencies', {})
                dev_deps = data.get('devDependencies', {})
                dependencies = list(deps.keys()) + list(dev_deps.keys())
            
            elif filename == 'requirements.txt':
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract package name (before ==, >=, etc.)
                        pkg_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].strip()
                        dependencies.append(pkg_name)
            
            elif filename == 'Pipfile':
                data = toml.loads(content)
                deps = data.get('packages', {})
                dev_deps = data.get('dev-packages', {})
                dependencies = list(deps.keys()) + list(dev_deps.keys())
            
            elif filename == 'pyproject.toml':
                data = toml.loads(content)
                # Poetry format
                if 'tool' in data and 'poetry' in data['tool']:
                    deps = data['tool']['poetry'].get('dependencies', {})
                    dev_deps = data['tool']['poetry'].get('dev-dependencies', {})
                    dependencies = list(deps.keys()) + list(dev_deps.keys())
            
            elif filename == 'go.mod':
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('require'):
                        continue
                    if line and not line.startswith('//'):
                        parts = line.split()
                        if parts:
                            # Extract module name
                            mod_name = parts[0].split('/')[-1]
                            dependencies.append(mod_name)
            
            elif filename == 'Cargo.toml':
                data = toml.loads(content)
                deps = data.get('dependencies', {})
                dev_deps = data.get('dev-dependencies', {})
                dependencies = list(deps.keys()) + list(dev_deps.keys())
            
            elif filename == 'Gemfile':
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('gem'):
                        # Extract gem name
                        parts = line.split("'")
                        if len(parts) >= 2:
                            dependencies.append(parts[1])
            
            elif filename == 'pom.xml':
                root = ET.fromstring(content)
                # Extract dependencies from Maven POM
                ns = {'maven': 'http://maven.apache.org/POM/4.0.0'}
                deps = root.findall('.//maven:dependency/maven:artifactId', ns)
                dependencies = [dep.text for dep in deps if dep.text]
            
        except Exception as e:
            logger.debug(f"Error parsing {filename}: {e}")
        
        return dependencies
    
    def get_comprehensive_data(self, username: str, top_repos_count: int = 10) -> Dict[str, Any]:
        """
        Main method to fetch all comprehensive data for a user
        Returns: Complete dataset for analysis
        """
        logger.info("=" * 50)
        logger.info(f"Starting comprehensive data fetch for: {username}")
        logger.info("=" * 50)
        
        # Check rate limit
        rate_limit = self.check_rate_limit()
        logger.info(f"API Rate Limit: {rate_limit['core_remaining']}/{rate_limit['core_limit']} remaining")
        
        # 1. Fetch profile
        profile = self.fetch_user_profile(username)
        
        # 2. Fetch repositories
        all_repos = self.fetch_repositories(limit=100)
        
        # 3. Get top active repos
        top_repos = self.get_top_active_repos(all_repos, count=top_repos_count)
        
        # 4. Fetch detailed data for top repos
        detailed_repos = []
        for repo in top_repos:
            logger.info(f"Analyzing repository: {repo['name']}")
            
            repo_detail = repo.copy()
            
            # Fetch package files
            package_files = list(PACKAGE_FILES.keys())
            files_content = self.fetch_repository_files(repo['full_name'], package_files)
            repo_detail['package_files'] = files_content
            
            # Parse dependencies
            dependencies = []
            for filename, content in files_content.items():
                deps = self.parse_package_file(filename, content)
                dependencies.extend(deps)
            repo_detail['dependencies'] = list(set(dependencies))  # Unique
            
            # Fetch commits (last 12 months)
            since_date = datetime.now() - timedelta(days=365)
            commits = self.fetch_commits(repo['full_name'], since_date=since_date)
            repo_detail['commits'] = commits
            
            # Fetch pull requests
            prs = self.fetch_pull_requests(repo['full_name'])
            repo_detail['pull_requests'] = prs
            
            # Fetch code reviews
            reviews = self.fetch_reviews_given(repo['full_name'])
            repo_detail['code_reviews'] = reviews
            
            # Check CI/CD
            cicd = self.check_cicd_presence(repo['full_name'])
            repo_detail['cicd_tools'] = cicd
            
            detailed_repos.append(repo_detail)
        
        # 5. Aggregate all data
        comprehensive_data = {
            'profile': profile,
            'all_repositories': all_repos,
            'top_repositories': detailed_repos,
            'fetched_at': datetime.now().isoformat(),
            'rate_limit': self.check_rate_limit(),
        }
        
        logger.info("=" * 50)
        logger.info("Data fetch complete!")
        logger.info("=" * 50)
        
        return comprehensive_data
