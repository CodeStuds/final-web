# 🚀 HireSight - Quick Start Guide

Get up and running in 5 minutes!

## ⚡ TL;DR

```bash
# 1. Start Backend
cd backend
./start.sh

# 2. Open Frontend
# Open in browser: DEVANGSHU_FRONTEND/COMPANY_MAIN_PAGE/index.html

# 3. Test
# Upload resumes, fill job details, click Submit!
```

## 📋 Prerequisites

- Python 3.8+ installed
- Modern web browser (Chrome, Firefox, Edge)
- Internet connection (for AI features)

## 🎯 Step-by-Step Setup

### Step 1: Start the Backend (30 seconds)

**On Linux/Mac:**
```bash
cd backend
chmod +x start.sh
./start.sh
```

**On Windows:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python api.py
```

**Expected Output:**
```
🚀 HireSight Unified API Server
📁 Upload folder: /path/to/uploads
📊 Max file size: 50.0 MB
✅ Allowed extensions: zip, pdf, docx, doc
Available endpoints:
  GET  /api/health - Health check
  POST /api/rank - Rank candidates from resumes
  ...
```

### Step 2: Verify Backend is Running (10 seconds)

Open in browser or use curl:
```
http://localhost:5000/api/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-29T...",
  "service": "HireSight API"
}
```

### Step 3: Open Frontend (10 seconds)

**Method 1 - Direct File Open:**
```bash
# From project root
cd DEVANGSHU_FRONTEND/COMPANY_MAIN_PAGE
# Then open index.html in your browser
```

**Method 2 - Simple HTTP Server:**
```bash
cd DEVANGSHU_FRONTEND/COMPANY_MAIN_PAGE
python -m http.server 8000
# Open: http://localhost:8000
```

### Step 4: Test the System (2 minutes)

1. **Fill in Job Details:**
   - Role: "Backend Developer"
   - Skills: "Python, Django, PostgreSQL"
   - Experience: Toggle "Yes" and set slider
   - CGPA: Toggle "Yes" and set slider

2. **Upload Resumes:**
   - Single file: Upload one .pdf or .docx
   - Multiple files: Upload a .zip containing multiple resumes

3. **Click Submit:**
   - Wait for processing (5-15 seconds)
   - View ranked candidates!

## 🎉 Success!

You should see:
- ✅ Ranked list of candidates
- ✅ Match scores (0-100)
- ✅ Skills matched
- ✅ Summary notes

## 🐛 Troubleshooting

### Backend Won't Start

**Error: "ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**Error: "Port already in use"**
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
# Or change port
export PORT=5001
python api.py
```

**Error: "Permission denied"**
```bash
chmod +x start.sh
```

### Frontend Shows Mock Data

**Symptom:** Results show "Source: mock (fallback used)"

**Solution:**
1. Check backend is running: `curl http://localhost:5000/api/health`
2. Check browser console for CORS errors
3. Verify API_BASE_URL in script.js: `http://localhost:5000/api`

### File Upload Fails

**Symptom:** "Invalid file type" or upload doesn't work

**Solutions:**
- ✅ Use supported formats: .zip, .pdf, .docx, .doc
- ✅ Check file size < 50MB
- ✅ Ensure backend has write permissions to `uploads/` folder

### No Results or Empty List

**Symptom:** Submit works but no candidates shown

**Solutions:**
- ✅ Check if resume has extractable text (not scanned image)
- ✅ Check backend terminal for error messages
- ✅ Try with a sample .txt file first
- ✅ Check browser console for JavaScript errors

## 🔧 Configuration

### Change Backend Port

```bash
export PORT=8080
python api.py
```

Then update frontend:
```javascript
// In script.js
const API_BASE_URL = "http://localhost:8080/api";
```

### Add GitHub Token (Optional)

For better GitHub analysis:
```bash
export GITHUB_TOKEN="ghp_your_token_here"
python api.py
```

Get token: https://github.com/settings/tokens

### Add Gemini API Key (Optional)

For interview question generation:
```bash
export GEMINI_API_KEY="your_key_here"
python api.py
```

Get key: https://aistudio.google.com/app/apikey

## 📖 Next Steps

Once everything works:

1. **Read Documentation:**
   - Backend API: `backend/README.md`
   - Integration: `INTEGRATION_GUIDE.md`
   - Overview: `PROJECT_OVERVIEW.md`

2. **Try Advanced Features:**
   - GitHub profile analysis
   - Interview question generation
   - Leaderboard with combined scores

3. **Deploy to Production:**
   - See deployment guide in `backend/README.md`
   - Update API_BASE_URL to your domain
   - Enable HTTPS

## 💡 Tips

- **Fast Testing:** Keep backend running while you test
- **Sample Data:** Use the mock data feature to test UI without backend
- **Browser DevTools:** F12 → Network tab to debug API calls
- **Backend Logs:** Watch terminal for processing details

## 🎓 Example Test Files

Create test files to experiment:

**test-resume.txt:**
```
John Doe
Backend Developer

Skills:
- Python (5 years)
- Django, Flask
- PostgreSQL, MongoDB
- Docker, AWS

Experience:
Software Engineer at Tech Corp (2020-2025)
- Developed REST APIs
- Led team of 5 developers
- Improved performance by 40%

Education:
BS Computer Science, GPA: 3.8/4.0
```

Save as .txt or .pdf and upload!

## 📊 What to Expect

**Processing Time:**
- Single resume: 1-3 seconds
- ZIP with 10 resumes: 5-10 seconds
- ZIP with 50 resumes: 20-30 seconds

**Accuracy:**
- Skill matching: ~90% for exact matches
- Score ranking: Based on TF-IDF similarity
- Best with well-formatted resumes

## ✅ Checklist

Before asking for help:

- [ ] Python 3.8+ installed: `python3 --version`
- [ ] Dependencies installed: `pip list | grep flask`
- [ ] Backend running: Visit `http://localhost:5000/api/health`
- [ ] Port 5000 free: `lsof -i :5000`
- [ ] Browser console checked: F12 → Console tab
- [ ] Valid file format: .pdf, .docx, .doc, .zip
- [ ] File size < 50MB
- [ ] Backend terminal checked for errors

## 🚀 Ready to Go!

That's it! You now have a fully functional candidate ranking system.

**Questions?** Check the detailed guides:
- `INTEGRATION_GUIDE.md` - Frontend integration
- `backend/README.md` - API documentation
- `PROJECT_OVERVIEW.md` - Full system overview

**Happy Hiring! 🎉**
