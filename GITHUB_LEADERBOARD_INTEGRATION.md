# GitHub Repository Leaderboard Integration

## Overview
The GitHub Repository Leaderboard feature has been successfully integrated into the HireSight platform. This feature allows companies to analyze and rank candidates based on their GitHub repositories and contributions.

## Features Added

### Backend Integration
- **New API Endpoint**: `/api/github/leaderboard`
- **Location**: `backend/api.py`
- **Functionality**: 
  - Analyzes multiple GitHub profiles simultaneously
  - Scores candidates based on repositories, skills, and job requirements
  - Integrates with Gemini AI for enhanced analysis (optional)
  - Returns structured leaderboard data with rankings

### Frontend Integration
- **UI Components**: New GitHub profile input section in COMPANY_MAIN_PAGE
- **Form Fields**:
  - Multi-line textarea for GitHub usernames/URLs
  - Checkbox to enable/disable Gemini AI analysis
  - Number input for repositories to analyze per candidate (1-20)
- **Display**: Beautiful leaderboard showing:
  - Candidate rankings with avatars
  - Comprehensive scoring metrics
  - Repository information
  - Matched skills
  - AI-generated insights (when enabled)

## How to Use

### For Companies

1. **Navigate to Company Dashboard** (`/COMPANY_MAIN_PAGE/`)

2. **Fill in Job Requirements**:
   - Enter the role you're hiring for
   - Specify required skills
   - Set CGPA and experience requirements (optional)
   - Add additional considerations

3. **Choose Analysis Method**:
   - **Option A**: Upload resume files/ZIP (existing feature)
   - **Option B**: Enter GitHub profiles (new feature)

4. **GitHub Profile Analysis**:
   - Enter GitHub usernames or profile URLs (one per line)
   - Examples:
     ```
     torvalds
     https://github.com/octocat
     github.com/username
     ```
   - Configure options:
     - ✓ Use AI-enhanced analysis (Gemini)
     - Set number of repositories to analyze (default: 5)

5. **Submit and View Results**:
   - Click "Submit Job Posting"
   - Wait for analysis to complete (may take 30-60 seconds)
   - View ranked candidates with detailed metrics

### API Request Format

```json
POST /api/github/leaderboard
Content-Type: application/json

{
  "github_profiles": [
    "torvalds",
    "https://github.com/octocat",
    "username3"
  ],
  "job_description": "Role: Senior Backend Developer\nRequired Skills: Python, Django, AWS\nMinimum CGPA: 7.5\nRequired Experience: 3 years\n\nAdditional Requirements:\nExperience with microservices and containerization",
  "top_n_repos": 5,
  "use_gemini": true
}
```

### API Response Format

```json
{
  "success": true,
  "candidates": [
    {
      "username": "username1",
      "name": "John Doe",
      "profile_url": "https://github.com/username1",
      "avatar_url": "https://avatars.githubusercontent.com/...",
      "total_score": 87.5,
      "ranking": 1,
      "metrics": {
        "skill_match_score": 85.0,
        "semantic_similarity_score": 90.0,
        "activity_score": 82.3,
        "community_score": 75.5,
        "code_quality_score": 88.2,
        "total_stars": 1500,
        "total_commits": 2500,
        "public_repos": 45,
        "followers": 250
      },
      "matching_skills": ["python", "django", "aws", "docker"],
      "top_repositories": [
        {
          "name": "awesome-project",
          "url": "https://github.com/username1/awesome-project",
          "description": "An awesome project",
          "stars": 500,
          "forks": 100,
          "language": "Python",
          "topics": ["django", "rest-api"]
        }
      ],
      "bio": "Software Engineer passionate about...",
      "location": "San Francisco, CA",
      "company": "Tech Company Inc",
      "gemini_fit_analysis": "This candidate shows strong...",
      "gemini_pattern_analysis": "Analysis of repository patterns..."
    }
  ],
  "job_description": "Role: Senior Backend Developer...",
  "analysis_summary": {
    "total_candidates": 3,
    "average_score": 75.2,
    "top_score": 87.5,
    "required_skills_identified": ["python", "django", "aws"],
    "most_common_languages": ["Python", "JavaScript", "Go"]
  },
  "timestamp": "2025-10-30T12:00:00.000Z"
}
```

## Scoring Methodology

The leaderboard uses a weighted scoring system:

- **30%** - Skill Match Score: How well candidate skills match job requirements
- **25%** - Semantic Similarity: Contextual match between profile and job description
- **20%** - Activity Score: Commits, contributions, and engagement
- **15%** - Community Score: Stars, forks, followers
- **10%** - Code Quality Score: Repository quality indicators

## Environment Variables Required

```bash
# Required
GITHUB_TOKEN=your_github_personal_access_token

# Optional (for AI-enhanced analysis)
GEMINI_API_KEY=your_gemini_api_key
```

## Files Modified

### Backend
- `backend/api.py` - Added `/api/github/leaderboard` endpoint and module imports

### Frontend
- `DEVANGSHU_FRONTEND/COMPANY_MAIN_PAGE/index.html` - Added GitHub profile input section
- `DEVANGSHU_FRONTEND/COMPANY_MAIN_PAGE/script.js` - Added GitHub leaderboard logic
- `DEVANGSHU_FRONTEND/COMPANY_MAIN_PAGE/style.css` - Added GitHub-specific styling
- `DEVANGSHU_FRONTEND/api-config.js` - Added `generateGitHubLeaderboard` API method

## Dependencies

The feature uses the existing `github-repo-leaderboard` module which requires:

```bash
PyGithub
google-generativeai
scikit-learn
numpy
```

These should already be installed if the backend is properly set up.

## Testing

### Manual Testing Steps

1. Start the backend server:
   ```bash
   cd backend
   python api.py
   ```

2. Open the frontend:
   ```
   http://localhost:5000/COMPANY_MAIN_PAGE/
   ```

3. Test with sample GitHub profiles:
   - Try with well-known profiles: `torvalds`, `octocat`
   - Test with private/non-existent profiles to verify error handling
   - Test with different numbers of profiles (1-10)

4. Verify the leaderboard displays:
   - Rankings are correct
   - All metrics are shown
   - Repository information is complete
   - AI analysis appears (if enabled)

### API Testing

```bash
# Test the endpoint directly
curl -X POST http://localhost:5000/api/github/leaderboard \
  -H "Content-Type: application/json" \
  -d '{
    "github_profiles": ["torvalds"],
    "job_description": "Looking for a senior C developer with Linux kernel experience",
    "top_n_repos": 5,
    "use_gemini": false
  }'
```

## Troubleshooting

### Common Issues

1. **"GITHUB_TOKEN not configured"**
   - Set the `GITHUB_TOKEN` environment variable with your GitHub Personal Access Token

2. **"GitHub Repo Leaderboard module not available"**
   - Ensure the `github-repo-leaderboard` folder exists in `backend/`
   - Check that all required Python packages are installed

3. **Rate Limit Errors**
   - GitHub API has rate limits
   - Use an authenticated token to get higher limits (5000 req/hour vs 60 req/hour)

4. **Slow Response Times**
   - Analysis can take 30-60 seconds for multiple profiles
   - Consider reducing `top_n_repos` for faster results
   - Disable Gemini analysis if speed is critical

## Future Enhancements

Potential improvements:

1. **Caching**: Cache GitHub profile data to reduce API calls
2. **Batch Processing**: Process profiles in parallel for faster results
3. **Advanced Filters**: Filter by language, stars, activity level
4. **Export**: Download leaderboard results as PDF/CSV
5. **Real-time Updates**: WebSocket for progress updates during analysis
6. **Comparison View**: Side-by-side candidate comparison

## Support

For issues or questions:
- Check the logs: `backend/hiresight.log`
- Review API documentation at: `http://localhost:5000/api/health`
- See `backend/github-repo-leaderboard/README.md` for module details

---

**Integration Complete**: All components are now working together seamlessly!
