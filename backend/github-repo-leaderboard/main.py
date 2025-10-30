from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn
import os
from dotenv import load_dotenv
from github_analyzer import GitHubAnalyzer
from leaderboard import LeaderboardGenerator
from gemini_analyzer import GeminiAnalyzer

# Load environment variables
load_dotenv()

app = FastAPI(
    title="GitHub Profile Leaderboard API",
    description="Analyze GitHub profiles and rank candidates based on their repositories",
    version="1.0.0"
)

class AnalyzeRequest(BaseModel):
    github_profiles: List[str] = Field(..., description="List of GitHub profile URLs or usernames")
    job_description: str = Field(..., description="Job description to match against")
    top_n_repos: Optional[int] = Field(5, description="Number of top repositories to analyze per user")
    use_gemini: Optional[bool] = Field(True, description="Use Gemini AI for enhanced analysis (requires GEMINI_API_KEY in .env)")

class CandidateScore(BaseModel):
    username: str
    profile_url: str
    total_score: float
    ranking: int
    metrics: dict
    top_repositories: List[dict]
    matching_skills: List[str]

class LeaderboardResponse(BaseModel):
    candidates: List[CandidateScore]
    job_description: str
    analysis_summary: dict

@app.get("/")
async def root():
    return {
        "message": "GitHub Profile Leaderboard API",
        "docs": "/docs",
        "endpoints": {
            "analyze": "/analyze - POST request to analyze GitHub profiles"
        }
    }

@app.post("/analyze", response_model=LeaderboardResponse)
async def analyze_profiles(request: AnalyzeRequest):
    """
    Analyze GitHub profiles and generate a leaderboard.

    This endpoint:
    1. Fetches user profiles and their repositories
    2. Analyzes top N repositories for each user using GitHub API
    3. Uses Gemini AI for intelligent code analysis
    4. Scores candidates based on multiple factors
    5. Matches skills against job description
    6. Returns a ranked leaderboard
    """
    try:
        # Get tokens from environment variables only
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise HTTPException(status_code=500, detail="GITHUB_TOKEN not found in environment variables. Please set it in .env file")

        gemini_key = os.getenv("GEMINI_API_KEY")

        # Initialize analyzers
        analyzer = GitHubAnalyzer(github_token)
        gemini_analyzer = None
        if request.use_gemini and gemini_key:
            try:
                gemini_analyzer = GeminiAnalyzer(gemini_key)
            except Exception as e:
                print(f"Warning: Could not initialize Gemini analyzer: {str(e)}")

        # Analyze all profiles
        candidate_data = []
        for profile in request.github_profiles:
            try:
                data = analyzer.analyze_profile(profile, request.top_n_repos)

                # Enhance with Gemini analysis if available
                if gemini_analyzer and data.get('top_repositories'):
                    try:
                        # Analyze each repository with Gemini
                        for repo in data['top_repositories']:
                            gemini_analysis = gemini_analyzer.analyze_repository_quality(repo)
                            repo['gemini_analysis'] = gemini_analysis

                        # Get candidate fit analysis
                        candidate_fit = gemini_analyzer.analyze_candidate_fit(data, request.job_description)
                        data['gemini_candidate_fit'] = candidate_fit

                        # Analyze repository patterns
                        repo_pattern_analysis = gemini_analyzer.analyze_multiple_repositories(data['top_repositories'])
                        data['gemini_pattern_analysis'] = repo_pattern_analysis

                    except Exception as e:
                        print(f"Gemini analysis failed for {profile}: {str(e)}")
                        data['gemini_analysis_error'] = str(e)

                candidate_data.append(data)
            except Exception as e:
                print(f"Error analyzing profile {profile}: {str(e)}")
                continue

        if not candidate_data:
            raise HTTPException(status_code=400, detail="No valid profiles could be analyzed")

        # Generate leaderboard with Gemini insights
        leaderboard_gen = LeaderboardGenerator(request.job_description, gemini_analyzer)
        leaderboard = leaderboard_gen.generate_leaderboard(candidate_data)

        return leaderboard

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
