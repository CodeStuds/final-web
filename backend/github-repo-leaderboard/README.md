# GitHub Profile Leaderboard API

An intelligent API that analyzes GitHub profiles and creates a ranked leaderboard of candidates based on their repositories, skills, and how well they match a given job description. **Now powered by Google Gemini AI** for advanced code quality analysis and candidate fit assessment.

## Features

- **Multi-Profile Analysis**: Analyze multiple GitHub profiles in a single request
- **Top Repository Analysis**: Examines the top 5 (configurable) repositories for each candidate
- **Gemini AI Integration**: Advanced AI-powered analysis including:
  - Repository code quality assessment (0-100 score)
  - Technical complexity evaluation
  - Candidate-job fit analysis with recommendations
  - Pattern recognition across repositories
  - Innovation and maintainability scoring
- **Intelligent Scoring System**: Ranks candidates based on:
  - Skill matching (30%): How well their skills match the job description
  - Semantic similarity (25%): Text analysis of profiles vs job description
  - Activity score (20%): Commits, contributions, and repository updates
  - Community engagement (15%): Followers, documentation quality
  - Code quality (10%): Stars, forks, maintenance, language diversity (enhanced by Gemini)
- **Skill Extraction**: Automatically identifies technical skills from job descriptions and profiles
- **Comprehensive Metrics**: Detailed breakdown of each candidate's strengths

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd github-repo-leaderboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your GitHub Personal Access Token:
     - Go to GitHub Settings → Developer settings → Personal access tokens
     - Generate a new token with `repo` and `user` scopes
   - (Optional but recommended) Add your Gemini API key:
     - Get one at https://makersuite.google.com/app/apikey
     - This enables AI-powered analysis for better insights

```bash
cp .env.example .env
# Edit .env and add your tokens
```

## Usage

### Starting the API Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Example Request

**Endpoint**: `POST /analyze`

**Request Body**:
```json
{
  "github_profiles": [
    "https://github.com/torvalds",
    "https://github.com/gvanrossum",
    "defunkt"
  ],
  "job_description": "Looking for a Python developer with experience in FastAPI, Docker, and CI/CD. Strong understanding of REST APIs and microservices architecture required. Experience with AWS and PostgreSQL is a plus.",
  "top_n_repos": 5,
  "use_gemini": true
}
```

**Note**: GitHub token and Gemini API key are now loaded from `.env` file for security.

**Response**:
```json
{
  "candidates": [
    {
      "username": "gvanrossum",
      "name": "Guido van Rossum",
      "profile_url": "https://github.com/gvanrossum",
      "avatar_url": "https://avatars.githubusercontent.com/...",
      "total_score": 87.5,
      "ranking": 1,
      "metrics": {
        "skill_match_score": 85.0,
        "semantic_similarity_score": 72.3,
        "activity_score": 65.8,
        "community_score": 92.1,
        "code_quality_score": 88.4,
        "total_stars": 1250,
        "total_commits": 3420,
        "public_repos": 45,
        "followers": 15000
      },
      "matching_skills": ["python", "fastapi", "docker", "rest", "api"],
      "top_repositories": [
        {
          "name": "cpython",
          "url": "https://github.com/python/cpython",
          "description": "The Python programming language",
          "stars": 50000,
          "forks": 25000,
          "commits": 500,
          "languages": ["Python", "C"],
          "topics": ["python", "programming-language"]
        }
      ],
      "bio": "Creator of Python programming language",
      "location": "California",
      "company": "Microsoft"
    }
  ],
  "job_description": "Looking for a Python developer...",
  "analysis_summary": {
    "total_candidates": 3,
    "average_score": 72.5,
    "top_score": 87.5,
    "required_skills_identified": ["python", "fastapi", "docker", "ci/cd", "rest", "api", "microservices", "aws", "postgresql"],
    "most_common_languages": ["Python", "JavaScript", "Go", "TypeScript"]
  }
}
```

### Using cURL

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "github_profiles": ["torvalds", "gvanrossum"],
    "job_description": "Python developer with FastAPI experience",
    "top_n_repos": 5,
    "use_gemini": true
  }'
```

### Using Python

```python
import requests

url = "http://localhost:8000/analyze"
payload = {
    "github_profiles": [
        "https://github.com/torvalds",
        "gvanrossum"
    ],
    "job_description": "Looking for a Python developer with FastAPI and Docker experience",
    "top_n_repos": 5,
    "use_gemini": True  # Enable Gemini AI analysis
}

response = requests.post(url, json=payload)
leaderboard = response.json()

print(f"Top Candidate: {leaderboard['candidates'][0]['username']}")
print(f"Score: {leaderboard['candidates'][0]['total_score']}")

# Access Gemini AI insights
if 'gemini_fit_analysis' in leaderboard['candidates'][0]:
    fit = leaderboard['candidates'][0]['gemini_fit_analysis']
    print(f"AI Recommendation: {fit['recommendation']}")
```

## Scoring Methodology

### 1. Skill Match Score (30% weight)
- Extracts technical skills from job description
- Compares against candidate's languages, topics, and bio
- Calculates percentage of required skills present

### 2. Semantic Similarity (25% weight)
- Uses TF-IDF vectorization and cosine similarity
- Compares job description with candidate's profile text
- Considers repository descriptions and topics

### 3. Activity Score (20% weight)
Factors:
- Total stars across repositories
- Total forks
- Total commits
- Contributions in last year
- Number of public repositories

### 4. Community Score (15% weight)
Factors:
- Number of followers
- Following ratio
- Documentation quality
- Repository descriptions

### 5. Code Quality Score (10% weight)
Factors:
- Average stars per repository
- Average forks per repository
- Recent maintenance activity
- Programming language diversity

## API Endpoints

### `GET /`
Health check and API information

### `POST /analyze`
Main endpoint for profile analysis

**Parameters**:
- `github_profiles` (required): List of GitHub usernames or profile URLs
- `github_token` (required): GitHub Personal Access Token
- `job_description` (required): Job description text
- `top_n_repos` (optional): Number of repositories to analyze per user (default: 5)

### `GET /health`
Server health check

## Rate Limits

GitHub API has rate limits:
- Authenticated requests: 5,000 per hour
- The API checks rate limits before processing

## Error Handling

The API handles various error scenarios:
- Invalid GitHub usernames
- Expired or invalid tokens
- Network issues
- Rate limit exceeded
- No valid profiles analyzed

## Requirements

- Python 3.8+
- GitHub Personal Access Token
- Internet connection

## Dependencies

See `requirements.txt` for full list:
- FastAPI: Web framework
- PyGithub: GitHub API client
- scikit-learn: Machine learning for similarity scoring
- Pydantic: Data validation
- uvicorn: ASGI server

## Future Enhancements

Potential improvements:
- Cache results to reduce API calls
- Add more sophisticated NLP for job description parsing
- Include contribution graph analysis
- Add code review quality metrics
- Support for private repositories
- Export results to PDF/Excel
- Real-time progress updates via WebSocket

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
