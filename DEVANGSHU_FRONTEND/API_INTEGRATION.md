# HireSight Frontend API Integration Guide

## Overview

The HireSight frontend is now fully integrated with the unified backend API. This document explains how the API integration works and how to use it.

## Files Structure

```
DEVANGSHU_FRONTEND/
├── api-config.js                    # Centralized API configuration
├── COMPANY_MAIN_PAGE/
│   ├── index.html                   # Main company page
│   └── script.js                    # Enhanced with API integration
└── API_INTEGRATION.md              # This file
```

## API Configuration

### Basic Setup

The API configuration is managed in `api-config.js`. This file provides:
- Centralized API endpoint configuration
- Automatic API key management
- Helper functions for all API operations
- Error handling

### Environment Variables

You can configure the API using environment variables:

```javascript
// Set these before loading the scripts
window.ENV = {
  API_BASE_URL: "http://localhost:5000/api",  // Your API URL
  API_KEY: "your-api-key-here"                 // Optional API key
};
```

Or they will default to:
- `API_BASE_URL`: `http://localhost:5000/api`
- `API_KEY`: (empty, optional)

## Available API Features

### 1. Resume Ranking (`/api/rank`)

**Purpose**: Rank multiple candidates based on uploaded resumes and job requirements.

**How to Use**:
1. Fill in the job posting form with role, skills, experience, and CGPA requirements
2. Upload a resume file (PDF, DOCX, DOC) or ZIP file with multiple resumes
3. Click "Submit Job Posting"
4. Results will be displayed with candidate rankings

**Features**:
- Automatic file processing
- Skill matching
- Score calculation
- Fallback to mock data if API is unavailable

### 2. Single Resume Analysis (`/api/analyze`)

**Purpose**: Analyze a single resume and get detailed scores.

**Features**:
- Keyword score
- Achievement score
- Formatting score
- Length score
- Overall main score

### 3. GitHub Profile Analysis (`/api/github/analyze`)

**Purpose**: Analyze a candidate's GitHub profile to assess technical skills.

**How to Use**:
1. After ranking candidates, click "Analyze GitHub" button for any candidate
2. Enter the candidate's GitHub username
3. View detailed analysis in a modal popup

**Features**:
- Repository analysis
- Language detection
- Contribution patterns
- Match score calculation (if job requirements provided)

### 4. Interview Question Generation (`/api/interview/generate`)

**Purpose**: Generate personalized interview questions based on candidate profile.

**How to Use**:
1. After ranking candidates, click "Generate Questions" button for any candidate
2. Choose to fetch profile from GitHub or enter manually
3. View generated questions in a modal popup
4. Copy questions to clipboard

**Features**:
- Technical questions based on skills
- Behavioral questions
- Personalized to candidate background
- Copy to clipboard functionality

### 5. Leaderboard (`/api/leaderboard`)

**Purpose**: Combine scores from multiple sources (LinkedIn, GitHub, Resume) into unified ranking.

**Status**: Available via API service, can be integrated as needed.

## Using the API Service

### Direct API Calls

The `HireSightAPI` object provides methods for all API operations:

```javascript
// Example: Analyze GitHub profile
try {
  const result = await HireSightAPI.analyzeGitHub('username', {
    role: 'Backend Developer',
    required_skills: ['Python', 'Django'],
    preferred_skills: ['Docker', 'AWS']
  });

  if (result.success) {
    console.log('Analysis:', result.analysis);
    console.log('Match Score:', result.match_score);
  }
} catch (error) {
  console.error('Error:', error.message);
}
```

```javascript
// Example: Generate interview questions
try {
  const result = await HireSightAPI.generateInterviewQuestions(
    'John Doe',
    'Experienced Python developer with 5 years...'
  );

  if (result.success) {
    console.log('Questions:', result.interview_questions);
  }
} catch (error) {
  console.error('Error:', error.message);
}
```

### API Methods

All methods are available through the `HireSightAPI` object:

- `checkHealth()` - Check API status
- `rankCandidates(formData)` - Rank candidates
- `analyzeResume(file)` - Analyze single resume
- `analyzeGitHub(username, jobRequirements)` - Analyze GitHub profile
- `generateInterviewQuestions(name, profile, apiKey)` - Generate questions
- `generateLeaderboard(candidates, weights)` - Create leaderboard

## User Interface Features

### Notifications

The integration includes a notification system that shows:
- Success messages (green)
- Warning messages (yellow)
- Error messages (red)
- Info messages (blue)

Notifications appear in the top-right corner and auto-dismiss after 5 seconds.

### Modal Dialogs

Results from GitHub analysis and interview generation are displayed in modal dialogs with:
- Clean, responsive design
- Close button
- Click-outside-to-close functionality
- Copy to clipboard for interview questions

### Action Buttons

Each ranked candidate has action buttons:
- **Analyze GitHub**: Opens GitHub profile analysis
- **Generate Questions**: Creates personalized interview questions

## Error Handling

The integration includes comprehensive error handling:

1. **Network Errors**: Gracefully falls back to mock data for ranking
2. **API Errors**: Shows user-friendly error messages
3. **Validation Errors**: Displays specific error from API
4. **Timeout Handling**: 30-second timeout for API calls

## Backend Requirements

Ensure the backend API is running:

```bash
cd backend
python api.py
```

The API should be accessible at `http://localhost:5000` by default.

### Environment Variables for Backend

Optional environment variables:
- `GITHUB_TOKEN` - GitHub Personal Access Token (for higher rate limits)
- `GEMINI_API_KEY` - Google Gemini API key (for interview questions)
- `PORT` - Server port (default: 5000)
- `DEBUG` - Debug mode (default: False)

## Testing

### Quick Test

1. Start the backend API:
   ```bash
   cd backend
   python api.py
   ```

2. Open `COMPANY_MAIN_PAGE/index.html` in a browser

3. Test the features:
   - Fill in job requirements
   - Upload a resume or ZIP file
   - Click "Submit Job Posting"
   - Use "Analyze GitHub" and "Generate Questions" buttons

### API Health Check

Open browser console and run:
```javascript
HireSightAPI.checkHealth().then(result => console.log(result));
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-29T...",
  "service": "HireSight API",
  "api_keys_enabled": false
}
```

## Troubleshooting

### API Not Loading

**Issue**: `HireSightAPI is undefined`

**Solution**:
- Ensure `api-config.js` is loaded before `script.js` in HTML
- Check browser console for script loading errors

### CORS Errors

**Issue**: Cross-Origin Request Blocked

**Solution**:
- Backend has CORS enabled by default
- If using different domain, update CORS settings in `backend/api.py`

### API Connection Failed

**Issue**: Network request failed or timeout

**Solution**:
- Check if backend is running: `http://localhost:5000/api/health`
- Verify `API_BASE_URL` in configuration
- Check firewall/network settings

### Fallback Data Showing

**Issue**: Seeing "⚠️ Fallback data used" message

**Solution**:
- Backend may not be running
- Check browser console for error details
- Verify API endpoint URLs

## Production Deployment

### Frontend Configuration

Set production API URL before loading scripts:

```html
<script>
  window.ENV = {
    API_BASE_URL: "https://your-api-domain.com/api",
    API_KEY: "your-production-api-key"
  };
</script>
<script src="../api-config.js"></script>
<script src="script.js"></script>
```

### Security Considerations

1. **API Keys**: Store API keys securely, not in client-side code
2. **HTTPS**: Use HTTPS in production
3. **CORS**: Configure CORS to allow only your frontend domain
4. **Rate Limiting**: Backend has built-in rate limiting
5. **Input Validation**: API validates all inputs

## Future Enhancements

Potential features to add:
- Real-time candidate comparison
- Bulk GitHub analysis
- LinkedIn integration
- Export results to PDF/CSV
- Candidate profile storage
- Interview scheduling

## Support

For issues or questions:
- Check backend logs: `backend/hiresight.log`
- Check browser console for errors
- Review API documentation: `backend/README.md`

## License

MIT License - See project root for details
