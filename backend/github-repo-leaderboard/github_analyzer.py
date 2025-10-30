from github import Github, GithubException
from typing import List, Dict, Optional
import re
from collections import Counter

class GitHubAnalyzer:
    """Analyzes GitHub profiles and repositories using the GitHub API."""

    def __init__(self, token: str):
        """
        Initialize the GitHub analyzer with a Personal Access Token.

        Args:
            token: GitHub Personal Access Token for API authentication
        """
        self.github = Github(token)
        self.rate_limit_check()

    def rate_limit_check(self):
        """Check GitHub API rate limit."""
        rate_limit = self.github.get_rate_limit()
        # Handle both old and new PyGithub API versions
        try:
            remaining = rate_limit.core.remaining
        except AttributeError:
            # For newer versions of PyGithub
            remaining = rate_limit.rate.remaining
        if remaining < 100:
            raise Exception(f"GitHub API rate limit too low: {remaining} requests remaining")

    def extract_username(self, profile_input: str) -> str:
        """
        Extract username from GitHub profile URL or username string.

        Args:
            profile_input: GitHub profile URL or username

        Returns:
            GitHub username
        """
        # Handle full URLs
        if "github.com" in profile_input:
            match = re.search(r"github\.com/([^/]+)", profile_input)
            if match:
                return match.group(1)
        # Handle direct username
        return profile_input.strip().strip("/")

    def analyze_profile(self, profile_input: str, top_n: int = 5) -> Dict:
        """
        Analyze a GitHub profile and extract relevant metrics.

        Args:
            profile_input: GitHub profile URL or username
            top_n: Number of top repositories to analyze

        Returns:
            Dictionary containing profile analysis data
        """
        username = self.extract_username(profile_input)

        try:
            user = self.github.get_user(username)
        except GithubException as e:
            raise Exception(f"Failed to fetch user {username}: {str(e)}")

        # Get user repositories
        repos = list(user.get_repos(sort="updated", direction="desc"))

        # Filter out forks if user has enough original repos
        original_repos = [r for r in repos if not r.fork]
        repos_to_analyze = original_repos if len(original_repos) >= top_n else repos

        # Get top N repositories by stars
        top_repos = sorted(repos_to_analyze, key=lambda x: x.stargazers_count, reverse=True)[:top_n]

        # Analyze repositories
        repo_analysis = []
        total_stars = 0
        total_forks = 0
        total_commits = 0
        languages_used = Counter()
        topics_used = Counter()

        for repo in top_repos:
            try:
                # Get repository metrics
                stars = repo.stargazers_count
                forks = repo.forks_count

                # Get commit count (limited to avoid rate limits)
                try:
                    commits = repo.get_commits().totalCount
                    # Cap at a reasonable number to avoid long API calls
                    commits = min(commits, 1000)
                except:
                    commits = 0

                # Get languages
                languages = repo.get_languages()
                for lang, bytes_count in languages.items():
                    languages_used[lang] += bytes_count

                # Get topics
                topics = repo.get_topics()
                for topic in topics:
                    topics_used[topic] += 1

                repo_data = {
                    "name": repo.name,
                    "url": repo.html_url,
                    "description": repo.description or "No description",
                    "stars": stars,
                    "forks": forks,
                    "commits": commits,
                    "languages": list(languages.keys()),
                    "topics": topics,
                    "created_at": repo.created_at.isoformat(),
                    "updated_at": repo.updated_at.isoformat(),
                    "open_issues": repo.open_issues_count,
                    "has_wiki": repo.has_wiki,
                    "has_documentation": repo.has_wiki or bool(repo.description),
                }

                repo_analysis.append(repo_data)
                total_stars += stars
                total_forks += forks
                total_commits += commits

            except Exception as e:
                print(f"Error analyzing repo {repo.name}: {str(e)}")
                continue

        # Get top languages (by byte count)
        top_languages = [lang for lang, _ in languages_used.most_common(10)]

        # Get profile metrics
        profile_data = {
            "username": username,
            "name": user.name or username,
            "profile_url": user.html_url,
            "avatar_url": user.avatar_url,
            "bio": user.bio or "",
            "company": user.company or "",
            "location": user.location or "",
            "email": user.email or "",
            "public_repos": user.public_repos,
            "followers": user.followers,
            "following": user.following,
            "created_at": user.created_at.isoformat(),
            "top_repositories": repo_analysis,
            "total_stars": total_stars,
            "total_forks": total_forks,
            "total_commits": total_commits,
            "languages": top_languages,
            "topics": [topic for topic, _ in topics_used.most_common(10)],
            "contributions_last_year": self._estimate_contributions(user, repos_to_analyze),
        }

        return profile_data

    def _estimate_contributions(self, user, repos: List) -> int:
        """
        Estimate yearly contributions based on recent repository activity.

        Args:
            user: GitHub user object
            repos: List of repository objects

        Returns:
            Estimated contribution count
        """
        # This is a simplified estimation
        # In production, you might want to scrape the contributions graph
        # or use a more sophisticated method
        contribution_estimate = 0

        for repo in repos[:10]:  # Limit to avoid rate limits
            try:
                # Get recent commits
                commits = list(repo.get_commits(author=user)[:100])
                contribution_estimate += len(commits)
            except:
                continue

        return contribution_estimate
