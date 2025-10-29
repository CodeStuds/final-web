# HireSight - Unified Backend API

A comprehensive Flask-based API that integrates all HireSight backend functionalities for candidate assessment, ranking, and analysis.

## 🎯 Features

- **Resume Scoring & Ranking**: Upload resumes (PDF, DOCX, ZIP) and rank candidates based on job requirements
- **GitHub Profile Analysis**: Analyze developer profiles from GitHub with skill matching
- **LinkedIn Data Processing**: Process LinkedIn profile data for candidate assessment
- **Interview Question Generation**: Generate personalized technical and behavioral interview questions using AI
- **Leaderboard System**: Combine scores from multiple sources to rank candidates

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables (optional):**
   ```bash
   export GITHUB_TOKEN="your_github_personal_access_token"
   export GEMINI_API_KEY="your_gemini_api_key"
   export PORT=5000
   export DEBUG=True
   ```

4. **Run the server:**
   ```bash
   python api.py
   ```

   Or with gunicorn for production:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 api:app
   ```

The API will be available at `http://localhost:5000`

## 📡 API Endpoints

### Health Check
```http
GET /api/health
```
Returns server status and timestamp.

### Rank Candidates
```http
POST /api/rank
Content-Type: multipart/form-data

Parameters:
- role (string): Job title
- skills (string): Required skills (comma-separated)
- experience (string): Required experience
- cgpa (string): Required CGPA
- additional (string): Additional requirements
- file (file): Resume file (.zip, .pdf, .docx, .doc)

Response:
{
  "success": true,
  "results": [
    {
      "name": "Candidate Name",
      "score": 85.5,
      "matchScore": 85.5,
      "skills": ["Python", "React"],
      "note": "Matched 5/6 required skills",
      "summary": "Resume score: 85.5/100"
    }
  ],
  "count": 10,
  "timestamp": "2025-10-29T10:30:00"
}
```

### Analyze Single Resume
```http
POST /api/analyze
Content-Type: multipart/form-data

Parameters:
- resume (file): Resume file (.pdf, .docx, .doc)

Response:
{
  "success": true,
  "mainScore": 84,
  "keywordScore": 78,
  "achievementScore": 88,
  "formattingScore": 90,
  "lengthScore": 76,
  "wordCount": 450,
  "timestamp": "2025-10-29T10:30:00"
}
```

### Analyze GitHub Profile
```http
POST /api/github/analyze
Content-Type: application/json

Body:
{
  "username": "github_username",
  "job_requirements": {
    "role": "Backend Developer",
    "required_skills": ["Python", "Django", "PostgreSQL"],
    "preferred_skills": ["Docker", "AWS"]
  }
}

Response:
{
  "success": true,
  "username": "github_username",
  "analysis": { ... },
  "match_score": 85.5,
  "timestamp": "2025-10-29T10:30:00"
}
```

### Generate Interview Questions
```http
POST /api/interview/generate
Content-Type: application/json

Body:
{
  "candidate_name": "John Doe",
  "candidate_profile": "Combined text from GitHub and LinkedIn...",
  "api_key": "optional_gemini_api_key"
}

Response:
{
  "success": true,
  "candidate_name": "John Doe",
  "interview_questions": "Generated interview guide...",
  "timestamp": "2025-10-29T10:30:00"
}
```

### Generate Leaderboard
```http
POST /api/leaderboard
Content-Type: application/json

Body:
{
  "candidates": [
    {
      "name": "John Doe",
      "linkedin_score": 85,
      "github_score": 90,
      "github_username": "johndoe"
    }
  ],
  "weights": {
    "linkedin": 0.5,
    "github": 0.5
  }
}

Response:
{
  "success": true,
  "leaderboard": [
    {
      "rank": 1,
      "name": "John Doe",
      "linkedin_score": 85,
      "github_score": 90,
      "combined_score": 87.5,
      "github_username": "johndoe"
    }
  ],
  "count": 1,
  "weights": {"linkedin": 0.5, "github": 0.5},
  "timestamp": "2025-10-29T10:30:00"
}
```

## 🔧 Configuration

### Frontend Integration

Update the frontend configuration in `DEVANGSHU_FRONTEND/COMPANY_MAIN_PAGE/script.js`:

```javascript
const API_BASE_URL = "http://localhost:5000/api"; // Update for production
```

### Environment Variables

- `GITHUB_TOKEN`: GitHub Personal Access Token for API access (optional but recommended)
- `GEMINI_API_KEY`: Google Gemini API key for interview question generation
- `PORT`: Server port (default: 5000)
- `DEBUG`: Debug mode (default: False)

## 📁 Project Structure

```
backend/
├── api.py                          # Main unified API server
├── requirements.txt                # Python dependencies
├── uploads/                        # Temporary file uploads (auto-created)
├── github-data-fetch/             # GitHub analysis modules
│   ├── data_fetcher.py
│   ├── analyzer.py
│   └── matcher.py
├── ibhanwork/                      # Resume scoring modules
│   ├── scorematcher.py
│   ├── qngenerator.py
│   └── textxtract.py
├── leaderboard/                    # Leaderboard generation
│   ├── leaderboard.py
│   └── data_loader.py
└── linkedin-data-fetch/            # LinkedIn data processing
    └── webhook_server.py
```

## 🧪 Testing

### Test with curl

**Health Check:**
```bash
curl http://localhost:5000/api/health
```

**Rank Candidates:**
```bash
curl -X POST http://localhost:5000/api/rank \
  -F "role=Backend Developer" \
  -F "skills=Python,Django,PostgreSQL" \
  -F "experience=2" \
  -F "cgpa=7.5" \
  -F "file=@resumes.zip"
```

**Analyze Resume:**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "resume=@resume.pdf"
```

### Test with Python

```python
import requests

# Rank candidates
with open('resumes.zip', 'rb') as f:
    response = requests.post('http://localhost:5000/api/rank', 
        data={
            'role': 'Backend Developer',
            'skills': 'Python,Django,PostgreSQL',
            'experience': '2',
            'cgpa': '7.5'
        },
        files={'file': f}
    )
    print(response.json())
```

## 🚢 Deployment

### Local Development
```bash
python api.py
```

### Production with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 api:app
```

### Docker (Optional)
Create a `Dockerfile`:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api:app"]
```

Build and run:
```bash
docker build -t hiresight-api .
docker run -p 5000:5000 hiresight-api
```

## 🔐 Security Notes

- Never commit API keys to version control
- Use environment variables for sensitive configuration
- Implement rate limiting for production deployment
- Add authentication/authorization for sensitive endpoints
- Validate and sanitize all user inputs
- Use HTTPS in production

## 🐛 Troubleshooting

**Import Errors:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (3.8+ required)

**File Upload Errors:**
- Check file size limits (default: 50MB)
- Verify file format is supported (.zip, .pdf, .docx, .doc)
- Ensure uploads directory has write permissions

**GitHub Analysis Errors:**
- Set `GITHUB_TOKEN` environment variable for higher rate limits
- Check network connectivity to GitHub API

**CORS Errors:**
- CORS is enabled for all origins in development
- Configure specific origins for production

## 📝 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 📧 Support

For issues or questions, please open a GitHub issue or contact the development team.
