from typing import List, Dict, Set
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class LeaderboardGenerator:
    """Generates a ranked leaderboard based on candidate profiles and job description."""

    def __init__(self, job_description: str, gemini_analyzer=None):
        """
        Initialize the leaderboard generator.

        Args:
            job_description: Job description to match candidates against
            gemini_analyzer: Optional GeminiAnalyzer instance for enhanced scoring
        """
        self.job_description = job_description
        self.required_skills = self._extract_skills(job_description)
        self.gemini_analyzer = gemini_analyzer

    def _extract_skills(self, text: str) -> Set[str]:
        """
        Extract technical skills and keywords from text.

        Args:
            text: Text to extract skills from

        Returns:
            Set of extracted skills
        """
        # Common programming languages and technologies
        common_skills = {
            'python', 'java', 'javascript', 'typescript', 'go', 'rust', 'c++', 'c#',
            'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab',
            'react', 'angular', 'vue', 'nodejs', 'django', 'flask', 'fastapi',
            'spring', 'express', 'laravel', 'rails',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
            'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'git', 'ci/cd', 'jenkins', 'github actions', 'gitlab',
            'machine learning', 'deep learning', 'ai', 'data science',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
            'rest', 'graphql', 'api', 'microservices', 'agile', 'scrum',
            'linux', 'unix', 'bash', 'shell', 'devops', 'sre',
            'html', 'css', 'sass', 'webpack', 'vite', 'next.js', 'gatsby',
        }

        text_lower = text.lower()
        found_skills = set()

        for skill in common_skills:
            if skill in text_lower or skill.replace(' ', '-') in text_lower:
                found_skills.add(skill)

        return found_skills

    def _calculate_skill_match_score(self, candidate_data: Dict) -> tuple[float, List[str]]:
        """
        Calculate how well candidate's skills match the job requirements.

        Args:
            candidate_data: Candidate profile data

        Returns:
            Tuple of (match_score, matching_skills)
        """
        # Extract candidate skills from languages, topics, and bio
        candidate_skills = set()

        # Add programming languages
        for lang in candidate_data.get('languages', []):
            candidate_skills.add(lang.lower())

        # Add topics
        for topic in candidate_data.get('topics', []):
            candidate_skills.add(topic.lower())

        # Extract from bio and company
        bio_text = f"{candidate_data.get('bio', '')} {candidate_data.get('company', '')}"
        candidate_skills.update(self._extract_skills(bio_text))

        # Calculate match
        matching_skills = candidate_skills.intersection(self.required_skills)

        if not self.required_skills:
            match_ratio = 0.5  # Neutral score if no skills detected
        else:
            match_ratio = len(matching_skills) / len(self.required_skills)

        return match_ratio, list(matching_skills)

    def _calculate_semantic_similarity(self, candidate_data: Dict) -> float:
        """
        Calculate semantic similarity between job description and candidate profile.

        Args:
            candidate_data: Candidate profile data

        Returns:
            Similarity score (0-1)
        """
        # Combine candidate information into text
        candidate_text = f"{candidate_data.get('bio', '')} "

        for repo in candidate_data.get('top_repositories', []):
            candidate_text += f"{repo.get('description', '')} "
            candidate_text += " ".join(repo.get('topics', []))
            candidate_text += " ".join(repo.get('languages', []))

        if not candidate_text.strip():
            return 0.0

        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            vectors = vectorizer.fit_transform([self.job_description, candidate_text])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return float(similarity)
        except:
            return 0.0

    def _calculate_activity_score(self, candidate_data: Dict) -> float:
        """
        Calculate activity score based on contributions, commits, and engagement.

        Args:
            candidate_data: Candidate profile data

        Returns:
            Activity score (0-100)
        """
        # Normalize metrics
        total_stars = min(candidate_data.get('total_stars', 0), 10000) / 10000
        total_forks = min(candidate_data.get('total_forks', 0), 5000) / 5000
        total_commits = min(candidate_data.get('total_commits', 0), 5000) / 5000
        contributions = min(candidate_data.get('contributions_last_year', 0), 2000) / 2000
        public_repos = min(candidate_data.get('public_repos', 0), 100) / 100

        # Weighted score
        activity_score = (
            total_stars * 0.25 +
            total_forks * 0.15 +
            total_commits * 0.25 +
            contributions * 0.25 +
            public_repos * 0.10
        ) * 100

        return activity_score

    def _calculate_community_score(self, candidate_data: Dict) -> float:
        """
        Calculate community engagement score.

        Args:
            candidate_data: Candidate profile data

        Returns:
            Community score (0-100)
        """
        followers = min(candidate_data.get('followers', 0), 5000) / 5000
        following = min(candidate_data.get('following', 0), 1000) / 1000

        # Check if repositories have good documentation
        repos = candidate_data.get('top_repositories', [])
        doc_count = sum(1 for repo in repos if repo.get('has_documentation', False))
        doc_ratio = doc_count / len(repos) if repos else 0

        community_score = (
            followers * 0.5 +
            (following * 0.2) +
            doc_ratio * 0.3
        ) * 100

        return community_score

    def _calculate_code_quality_score(self, candidate_data: Dict) -> float:
        """
        Estimate code quality based on available metrics.

        Args:
            candidate_data: Candidate profile data

        Returns:
            Code quality score (0-100)
        """
        repos = candidate_data.get('top_repositories', [])

        if not repos:
            return 0.0

        # Calculate average stars per repo
        avg_stars = sum(repo.get('stars', 0) for repo in repos) / len(repos)
        stars_score = min(avg_stars, 500) / 500

        # Calculate average forks per repo
        avg_forks = sum(repo.get('forks', 0) for repo in repos) / len(repos)
        forks_score = min(avg_forks, 200) / 200

        # Check for active maintenance (recent updates)
        recent_count = sum(1 for repo in repos if repo.get('updated_at', ''))
        maintenance_score = recent_count / len(repos)

        # Language diversity
        all_languages = set()
        for repo in repos:
            all_languages.update(repo.get('languages', []))
        diversity_score = min(len(all_languages), 10) / 10

        # If Gemini analysis is available, incorporate it
        gemini_quality_boost = 0
        if repos:
            gemini_scores = []
            for repo in repos:
                if 'gemini_analysis' in repo and 'quality_score' in repo['gemini_analysis']:
                    gemini_scores.append(repo['gemini_analysis']['quality_score'])

            if gemini_scores:
                avg_gemini_score = sum(gemini_scores) / len(gemini_scores)
                gemini_quality_boost = avg_gemini_score / 100  # Normalize to 0-1

        quality_score = (
            stars_score * 0.25 +
            forks_score * 0.15 +
            maintenance_score * 0.25 +
            diversity_score * 0.15 +
            gemini_quality_boost * 0.20  # 20% weight on Gemini analysis
        ) * 100

        return quality_score

    def generate_leaderboard(self, candidates_data: List[Dict]) -> Dict:
        """
        Generate a ranked leaderboard of candidates.

        Args:
            candidates_data: List of candidate profile data dictionaries

        Returns:
            Leaderboard dictionary with ranked candidates
        """
        scored_candidates = []

        for candidate in candidates_data:
            # Calculate individual scores
            skill_match, matching_skills = self._calculate_skill_match_score(candidate)
            semantic_similarity = self._calculate_semantic_similarity(candidate)
            activity_score = self._calculate_activity_score(candidate)
            community_score = self._calculate_community_score(candidate)
            quality_score = self._calculate_code_quality_score(candidate)

            # Calculate weighted total score (out of 100)
            total_score = (
                skill_match * 30 +           # 30% weight on skill matching
                semantic_similarity * 25 +    # 25% weight on semantic similarity
                activity_score * 0.20 +       # 20% weight on activity
                community_score * 0.15 +      # 15% weight on community
                quality_score * 0.10          # 10% weight on code quality
            )

            candidate_result = {
                "username": candidate['username'],
                "name": candidate['name'],
                "profile_url": candidate['profile_url'],
                "avatar_url": candidate.get('avatar_url', ''),
                "total_score": round(total_score, 2),
                "metrics": {
                    "skill_match_score": round(skill_match * 100, 2),
                    "semantic_similarity_score": round(semantic_similarity * 100, 2),
                    "activity_score": round(activity_score, 2),
                    "community_score": round(community_score, 2),
                    "code_quality_score": round(quality_score, 2),
                    "total_stars": candidate.get('total_stars', 0),
                    "total_commits": candidate.get('total_commits', 0),
                    "public_repos": candidate.get('public_repos', 0),
                    "followers": candidate.get('followers', 0),
                },
                "matching_skills": matching_skills,
                "top_repositories": candidate.get('top_repositories', [])[:5],
                "bio": candidate.get('bio', ''),
                "location": candidate.get('location', ''),
                "company": candidate.get('company', ''),
            }

            # Add Gemini insights if available
            if 'gemini_candidate_fit' in candidate:
                candidate_result['gemini_fit_analysis'] = candidate['gemini_candidate_fit']

            if 'gemini_pattern_analysis' in candidate:
                candidate_result['gemini_pattern_analysis'] = candidate['gemini_pattern_analysis']

            scored_candidates.append(candidate_result)

        # Sort by total score descending
        scored_candidates.sort(key=lambda x: x['total_score'], reverse=True)

        # Add ranking
        for idx, candidate in enumerate(scored_candidates, 1):
            candidate['ranking'] = idx

        # Generate summary statistics
        if scored_candidates:
            summary = {
                "total_candidates": len(scored_candidates),
                "average_score": round(np.mean([c['total_score'] for c in scored_candidates]), 2),
                "top_score": scored_candidates[0]['total_score'] if scored_candidates else 0,
                "required_skills_identified": list(self.required_skills),
                "most_common_languages": self._get_top_languages(candidates_data),
            }
        else:
            summary = {
                "total_candidates": 0,
                "average_score": 0,
                "top_score": 0,
                "required_skills_identified": list(self.required_skills),
                "most_common_languages": [],
            }

        return {
            "candidates": scored_candidates,
            "job_description": self.job_description,
            "analysis_summary": summary,
        }

    def _get_top_languages(self, candidates_data: List[Dict]) -> List[str]:
        """Get most common programming languages across all candidates."""
        language_counter = Counter()

        for candidate in candidates_data:
            for lang in candidate.get('languages', []):
                language_counter[lang] += 1

        return [lang for lang, _ in language_counter.most_common(10)]
