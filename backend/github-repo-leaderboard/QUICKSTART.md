# Quick Start Guide

Get the GitHub Profile Leaderboard API up and running in 5 minutes!

## Prerequisites

- Python 3.8+ or Conda/Miniconda
- GitHub Personal Access Token
- (Optional) Gemini API Key for AI-powered analysis

## Step 1: Install Dependencies

### Using Conda (Recommended)
```bash
conda activate hack  # or your conda environment name
pip install -r requirements.txt
```

### Using pip
```bash
pip install -r requirements.txt
```

## Step 2: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your tokens:
```bash
# Required: Get from https://github.com/settings/tokens
GITHUB_TOKEN=ghp_your_token_here

# Optional but recommended: Get from https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_key_here
```

## Step 3: Start the API Server

### Using Conda
```bash
conda activate hack
python main.py
```

### Using Python directly
```bash
python main.py
```

The API will start on `http://localhost:8000`

## Step 4: Test the API

### Option 1: Interactive Documentation
Open your browser and go to:
- Swagger UI: http://localhost:8000/docs
- Try the `/analyze` endpoint directly in the browser

### Option 2: Use the Example Script
```bash
python example_request.py
```

### Option 3: cURL Command
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "github_profiles": ["torvalds", "gvanrossum"],
    "job_description": "Looking for a Python expert with systems programming experience",
    "top_n_repos": 5,
    "use_gemini": true
  }'
```

## Example API Request

```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={
        "github_profiles": [
            "torvalds",
            "gvanrossum",
            "dhh"
        ],
        "job_description": """
            Senior Backend Developer needed.
            Required: Python, REST APIs, Docker
            Nice to have: Kubernetes, AWS, PostgreSQL
        """,
        "top_n_repos": 5,
        "use_gemini": True
    }
)

result = response.json()

# Print leaderboard
for candidate in result['candidates']:
    print(f"#{candidate['ranking']} - {candidate['name']}")
    print(f"   Score: {candidate['total_score']}/100")
    print(f"   Skills: {', '.join(candidate['matching_skills'][:5])}")

    # Gemini AI insights (if available)
    if 'gemini_fit_analysis' in candidate:
        fit = candidate['gemini_fit_analysis']
        print(f"   AI Recommendation: {fit['recommendation']}")
    print()
```

## What the API Does

1. **Fetches GitHub Data**: Uses the GitHub API to pull:
   - User profile information
   - Top repositories (by stars)
   - Languages, topics, commit counts
   - Stars, forks, and engagement metrics

2. **Analyzes with AI** (if Gemini enabled):
   - Evaluates code quality of each repository
   - Assesses technical complexity
   - Determines candidate-job fit
   - Identifies patterns across projects

3. **Scores Candidates** based on:
   - Skill matching (30%)
   - Semantic similarity to job description (25%)
   - GitHub activity (20%)
   - Community engagement (15%)
   - Code quality (10%)

4. **Returns Ranked Leaderboard**:
   - Sorted by total score
   - Detailed metrics for each candidate
   - AI-powered insights
   - Repository highlights

## Response Structure

```json
{
  "candidates": [
    {
      "ranking": 1,
      "username": "gvanrossum",
      "total_score": 87.5,
      "metrics": {
        "skill_match_score": 85.0,
        "activity_score": 75.3,
        "code_quality_score": 92.1
      },
      "matching_skills": ["python", "programming-languages"],
      "gemini_fit_analysis": {
        "overall_fit_score": 88,
        "recommendation": "Strong Fit",
        "standout_qualities": ["Language design expertise", "Long-term project maintenance"]
      },
      "top_repositories": [...]
    }
  ],
  "analysis_summary": {
    "total_candidates": 3,
    "average_score": 72.5,
    "top_score": 87.5
  }
}
```

## Troubleshooting

### "GITHUB_TOKEN not found"
- Make sure you created the `.env` file
- Verify GITHUB_TOKEN is set in `.env`
- Restart the API server after adding the token

### "Port 8000 already in use"
- Kill existing process: `pkill -f "python.*main.py"`
- Or change port in `main.py`: `uvicorn.run(app, port=8001)`

### API is slow
- This is normal! The API:
  - Fetches data from GitHub API (rate limited)
  - Analyzes multiple repositories
  - Runs AI analysis (if Gemini enabled)
- For 3 profiles with 5 repos each: expect 30-60 seconds

### Gemini analysis not showing
- Verify `GEMINI_API_KEY` is in `.env`
- Set `"use_gemini": true` in request
- Check API quota at https://makersuite.google.com/

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the interactive API docs at http://localhost:8000/docs
- Customize scoring weights in `leaderboard.py`
- Add more skills to detect in `leaderboard.py`

## Need Help?

- Check the API logs for detailed error messages
- Verify your tokens are valid
- Ensure you have internet connectivity for API calls
- See [README.md](README.md) for more details
