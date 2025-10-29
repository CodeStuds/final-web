# Frontend Integration Guide

This guide explains how to integrate the HireSight backend API with your frontend application.

## 🔗 Quick Setup

### 1. Update API Configuration

The frontend is already configured to work with the unified backend API. The configuration is in:
- `DEVANGSHU_FRONTEND/COMPANY_MAIN_PAGE/script.js`

**Current Configuration:**
```javascript
const API_BASE_URL = "http://localhost:5000/api";
```

**For Production:**
```javascript
const API_BASE_URL = "https://your-domain.com/api";
```

### 2. Start the Backend Server

```bash
cd backend
./start.sh
```

Or manually:
```bash
cd backend
python api.py
```

### 3. Open the Frontend

Simply open the HTML files in your browser:
- Company Registration: `DEVANGSHU_FRONTEND/COMPANY_REGISTRATION/index.html`
- Company Login: `DEVANGSHU_FRONTEND/COMPANY_LOGIN/index.html`
- Company Main Page: `DEVANGSHU_FRONTEND/COMPANY_MAIN_PAGE/index.html`

## 📋 What Was Changed

### Minimal Frontend Changes (Design Preserved)

Only the API endpoints were updated to use the new unified backend:

1. **API Base URL**: Changed from placeholder to `http://localhost:5000/api`
2. **Request Timeout**: Increased to 15 seconds for file processing
3. **Form Data Collection**: Enhanced to capture all job requirements (experience, CGPA, etc.)
4. **Authorization Header**: Removed (can be added later if needed)

### New Features Available

The frontend now has access to:

✅ **Candidate Ranking** - Upload resumes and get ranked results
✅ **Resume Analysis** - Get detailed scores for individual resumes
✅ **GitHub Integration** - Analyze developer profiles (can be added to UI)
✅ **Interview Questions** - Generate personalized questions (can be added to UI)
✅ **Leaderboard** - Combined scoring from multiple sources (can be added to UI)

## 🎯 How It Works

### Job Posting & Candidate Ranking

**Frontend Form** → **Backend API** → **Results Display**

1. User fills out the job posting form:
   - Role (e.g., "Backend Developer")
   - Required skills (e.g., "Python, Django, PostgreSQL")
   - Experience requirement (Yes/No + slider)
   - CGPA requirement (Yes/No + slider)
   - Additional requirements (text)
   - Resume file(s) (.zip, .pdf, .docx, .doc)

2. Frontend sends data to `/api/rank`

3. Backend processes:
   - Extracts text from resumes
   - Calculates similarity scores using TF-IDF
   - Matches skills from job requirements
   - Ranks candidates by score

4. Frontend displays results:
   - Ranked list of candidates
   - Match scores
   - Matched skills
   - Summary notes

### Resume Analysis

**Upload Resume** → **Backend Analysis** → **Score Breakdown**

1. User uploads a single resume
2. Frontend sends to `/api/analyze`
3. Backend calculates:
   - Main score (0-100)
   - Keyword score
   - Achievement score
   - Formatting score
   - Length score
4. Frontend displays score breakdown with progress bars

## 🔄 API Request Examples

### Rank Candidates

```javascript
// Collect form data
const formData = new FormData();
formData.append('role', 'Backend Developer');
formData.append('skills', 'Python,Django,PostgreSQL');
formData.append('experience', '2'); // years
formData.append('cgpa', '7.5');
formData.append('additional', 'Experience with REST APIs preferred');
formData.append('file', resumeFile); // File object

// Send request
const response = await fetch('http://localhost:5000/api/rank', {
  method: 'POST',
  body: formData
});

const data = await response.json();
// data.results contains ranked candidates
```

### Analyze Single Resume

```javascript
const formData = new FormData();
formData.append('resume', resumeFile);

const response = await fetch('http://localhost:5000/api/analyze', {
  method: 'POST',
  body: formData
});

const scores = await response.json();
// scores.mainScore, scores.keywordScore, etc.
```

### Analyze GitHub Profile

```javascript
const response = await fetch('http://localhost:5000/api/github/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'github_username',
    job_requirements: {
      role: 'Backend Developer',
      required_skills: ['Python', 'Django'],
      preferred_skills: ['Docker', 'AWS']
    }
  })
});

const analysis = await response.json();
// analysis.match_score, analysis.analysis, etc.
```

## 🎨 Adding New Features to UI

### Example: Add GitHub Analysis Button

1. **Add HTML Button:**
```html
<button class="btn btn-primary" id="analyzeGithubBtn">
  Analyze GitHub Profile
</button>
<input type="text" id="githubUsername" placeholder="GitHub username">
```

2. **Add JavaScript Handler:**
```javascript
document.getElementById('analyzeGithubBtn').addEventListener('click', async () => {
  const username = document.getElementById('githubUsername').value;
  
  try {
    const response = await fetch(`${API_BASE_URL}/github/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: username,
        job_requirements: {
          role: 'Backend Developer',
          required_skills: ['Python', 'Django']
        }
      })
    });
    
    const data = await response.json();
    console.log('GitHub Analysis:', data);
    // Display results in UI
  } catch (error) {
    console.error('Error:', error);
  }
});
```

## 🛡️ Error Handling

The frontend includes fallback to mock data if the backend is unavailable:

```javascript
try {
  const res = await fetchRank(formData);
  renderResults(res.data, { source: 'backend' });
} catch (err) {
  console.warn('Backend unavailable, using fallback:', err);
  const fallback = mockDataset();
  renderResults(fallback, { source: 'mock', fallback: true });
}
```

This ensures the UI always works, even during development without the backend running.

## 🔧 Troubleshooting

### CORS Errors

If you see CORS errors in the browser console:

1. **Check backend is running**: Visit `http://localhost:5000/api/health`
2. **CORS is enabled**: The backend has `flask-cors` installed and configured
3. **Use correct URL**: Make sure `API_BASE_URL` matches your backend

### File Upload Errors

- **Max file size**: Default is 50MB, check `MAX_FILE_SIZE` in backend
- **Supported formats**: .zip, .pdf, .docx, .doc
- **Check file permissions**: Ensure backend can write to `uploads/` directory

### No Results Returned

- **Check console**: Open browser DevTools → Console tab
- **Check network tab**: See actual request/response
- **Try with single resume**: Test with one PDF file first
- **Check backend logs**: Terminal where `api.py` is running

## 🚀 Production Deployment

### 1. Update Frontend URL

```javascript
// In script.js, change:
const API_BASE_URL = "https://api.yourdomain.com/api";
```

### 2. Deploy Backend

Options:
- **Heroku**: `git push heroku main`
- **DigitalOcean**: Docker container
- **AWS EC2**: Nginx + Gunicorn
- **Render.com**: One-click deploy

### 3. Update CORS Settings

In `api.py`, configure allowed origins:
```python
from flask_cors import CORS
CORS(app, origins=["https://yourdomain.com"])
```

### 4. Enable HTTPS

- Use SSL certificates (Let's Encrypt)
- Update all URLs to `https://`
- Configure secure headers

## 📊 Performance Tips

1. **File Size Optimization**
   - Compress large PDF files
   - Use .zip for multiple resumes
   - Set reasonable file size limits

2. **Caching**
   - Backend caches GitHub API results
   - Consider browser caching for static assets

3. **Loading States**
   - Show spinners during API calls
   - Disable submit buttons to prevent double-clicks
   - Display progress for large file uploads

4. **Pagination**
   - For large candidate lists, implement pagination
   - Load results in batches

## 🧪 Testing

### Manual Testing

1. **Test Health Endpoint:**
   - Visit: `http://localhost:5000/api/health`
   - Should return JSON with status "healthy"

2. **Test File Upload:**
   - Open Company Main Page
   - Fill in job details
   - Upload a sample resume
   - Check results display

3. **Test Error Handling:**
   - Stop backend server
   - Try submitting form
   - Should show fallback mock data

### Automated Testing (Optional)

Add frontend tests using Jest or similar:
```javascript
test('API integration', async () => {
  const formData = new FormData();
  formData.append('role', 'Developer');
  
  const response = await fetch('http://localhost:5000/api/rank', {
    method: 'POST',
    body: formData
  });
  
  expect(response.ok).toBe(true);
});
```

## 📝 Summary

✅ **Backend**: Unified API with all features integrated
✅ **Frontend**: Minimal changes, design preserved
✅ **Integration**: Working end-to-end with error handling
✅ **Extensible**: Easy to add new features
✅ **Production-ready**: Deployment guide included

The system is now fully integrated and ready to use! 🎉
