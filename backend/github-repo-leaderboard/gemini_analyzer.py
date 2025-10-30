import google.generativeai as genai
from typing import Dict, List, Optional
import json

class GeminiAnalyzer:
    """Uses Gemini API to analyze repository code and provide intelligent insights."""

    def __init__(self, api_key: str):
        """
        Initialize Gemini analyzer.

        Args:
            api_key: Google Gemini API key
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def analyze_repository_quality(self, repo_data: Dict) -> Dict:
        """
        Analyze repository code quality and provide insights using Gemini.

        Args:
            repo_data: Repository information including name, description, languages, etc.

        Returns:
            Dictionary with Gemini analysis results
        """
        prompt = f"""
        Analyze this GitHub repository and provide insights:

        Repository: {repo_data.get('name')}
        Description: {repo_data.get('description', 'No description')}
        Languages: {', '.join(repo_data.get('languages', []))}
        Stars: {repo_data.get('stars', 0)}
        Forks: {repo_data.get('forks', 0)}
        Topics: {', '.join(repo_data.get('topics', []))}

        Provide a JSON response with:
        1. quality_score (0-100): Overall code quality assessment
        2. key_strengths: List of 3 main strengths
        3. technical_complexity: Rating (Low/Medium/High)
        4. maintainability_score (0-100): How well maintained the project appears
        5. innovation_score (0-100): Level of technical innovation
        6. brief_summary: 2-sentence summary of the repository's purpose and quality

        Return only valid JSON, no other text.
        """

        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip().replace('```json', '').replace('```', '').strip())
            return result
        except Exception as e:
            # Fallback if Gemini fails
            return {
                "quality_score": 50,
                "key_strengths": ["Open source project", "Active development"],
                "technical_complexity": "Medium",
                "maintainability_score": 50,
                "innovation_score": 50,
                "brief_summary": f"Repository {repo_data.get('name')} with {len(repo_data.get('languages', []))} programming languages.",
                "error": str(e)
            }

    def analyze_candidate_fit(self, candidate_data: Dict, job_description: str) -> Dict:
        """
        Use Gemini to analyze how well a candidate fits a job description.

        Args:
            candidate_data: Candidate's GitHub profile data
            job_description: Job description text

        Returns:
            Dictionary with fit analysis
        """
        # Prepare candidate summary
        repos_summary = []
        for repo in candidate_data.get('top_repositories', [])[:3]:
            repos_summary.append(
                f"- {repo.get('name')}: {repo.get('description', 'N/A')} "
                f"({repo.get('stars')} stars, Languages: {', '.join(repo.get('languages', [])[:3])})"
            )

        prompt = f"""
        Job Description:
        {job_description}

        Candidate Profile:
        Username: {candidate_data.get('username')}
        Bio: {candidate_data.get('bio', 'No bio')}
        Location: {candidate_data.get('location', 'Not specified')}
        Company: {candidate_data.get('company', 'Not specified')}
        Public Repos: {candidate_data.get('public_repos', 0)}
        Followers: {candidate_data.get('followers', 0)}
        Total Stars: {candidate_data.get('total_stars', 0)}
        Languages: {', '.join(candidate_data.get('languages', [])[:8])}

        Top Repositories:
        {chr(10).join(repos_summary)}

        Analyze this candidate's fit for the job and provide a JSON response with:
        1. overall_fit_score (0-100): How well they match the job
        2. matching_requirements: List of job requirements they meet
        3. missing_requirements: List of job requirements they might lack
        4. standout_qualities: 3 qualities that make them stand out
        5. red_flags: Any concerns (empty list if none)
        6. recommendation: "Strong Fit", "Good Fit", "Moderate Fit", or "Weak Fit"
        7. summary: 3-sentence analysis of their candidacy

        Return only valid JSON, no other text.
        """

        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip().replace('```json', '').replace('```', '').strip())
            return result
        except Exception as e:
            return {
                "overall_fit_score": 50,
                "matching_requirements": ["Programming experience"],
                "missing_requirements": ["Unable to determine"],
                "standout_qualities": ["Active GitHub profile", "Multiple repositories", "Open source contributor"],
                "red_flags": [],
                "recommendation": "Moderate Fit",
                "summary": f"Candidate {candidate_data.get('username')} shows development experience with {candidate_data.get('public_repos', 0)} repositories. Further review recommended.",
                "error": str(e)
            }

    def analyze_multiple_repositories(self, repos: List[Dict]) -> Dict:
        """
        Analyze multiple repositories together for patterns and overall assessment.

        Args:
            repos: List of repository data dictionaries

        Returns:
            Overall analysis across repositories
        """
        repos_text = []
        for repo in repos[:5]:
            repos_text.append(
                f"- {repo.get('name')}: {repo.get('description', 'N/A')} "
                f"(Stars: {repo.get('stars')}, Languages: {', '.join(repo.get('languages', [])[:3])})"
            )

        prompt = f"""
        Analyze these GitHub repositories from a single developer:

        {chr(10).join(repos_text)}

        Provide a JSON response with:
        1. coding_style_consistency (0-100): How consistent their coding approach is
        2. domain_expertise: List of technical domains they excel in
        3. project_diversity_score (0-100): Variety in project types
        4. leadership_indicators: Signs of technical leadership (list)
        5. learning_trajectory: "Rapid Growth", "Steady Progress", "Experienced", or "Varied"
        6. overall_assessment: 2-sentence summary

        Return only valid JSON, no other text.
        """

        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip().replace('```json', '').replace('```', '').strip())
            return result
        except Exception as e:
            return {
                "coding_style_consistency": 70,
                "domain_expertise": ["Software Development"],
                "project_diversity_score": 60,
                "leadership_indicators": ["Multiple projects"],
                "learning_trajectory": "Steady Progress",
                "overall_assessment": "Developer shows consistent contribution patterns across multiple repositories.",
                "error": str(e)
            }

    def generate_hiring_recommendation(self, all_analysis: Dict) -> str:
        """
        Generate a final hiring recommendation based on all analysis data.

        Args:
            all_analysis: Combined analysis data

        Returns:
            Detailed hiring recommendation text
        """
        prompt = f"""
        Based on this comprehensive candidate analysis, provide a hiring recommendation:

        {json.dumps(all_analysis, indent=2)}

        Provide a clear, professional hiring recommendation that includes:
        1. Overall verdict (Highly Recommend / Recommend / Consider / Do Not Recommend)
        2. Key strengths (3-4 bullet points)
        3. Areas of concern (if any)
        4. Best role fit
        5. Interview focus areas

        Format as a professional HR report.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Analysis complete. Review candidate profile for detailed metrics. Error: {str(e)}"
