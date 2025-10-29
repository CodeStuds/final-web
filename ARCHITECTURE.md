# HireSight Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                           │
│                    (HTML/CSS/JavaScript)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐ │
│  │  Home Page     │  │  Registration  │  │  Login Page      │ │
│  │                │  │  Page          │  │                  │ │
│  └────────────────┘  └────────────────┘  └──────────────────┘ │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Company Main Page (Job Posting)                  │  │
│  │  • Upload resumes                                        │  │
│  │  • Define job requirements                               │  │
│  │  • View ranked candidates                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│                  API_BASE_URL = "localhost:5000/api"            │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                │ HTTP/JSON
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      UNIFIED API LAYER                           │
│                    Flask Backend (api.py)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Endpoints:                                                      │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ GET  /api/health          → Server health check        │    │
│  │ POST /api/rank            → Rank candidates            │    │
│  │ POST /api/analyze         → Analyze single resume      │    │
│  │ POST /api/github/analyze  → GitHub profile analysis    │    │
│  │ POST /api/interview/generate → Generate questions      │    │
│  │ POST /api/leaderboard     → Combined rankings          │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Features:                                                       │
│  • CORS enabled for cross-origin requests                       │
│  • File upload handling (ZIP, PDF, DOCX)                        │
│  • Error handling with graceful fallbacks                       │
│  • Request validation and sanitization                          │
│                                                                  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                │ Function Calls
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PROCESSING MODULES                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐ │
│  │ Resume Scorer  │  │ GitHub Fetcher │  │ LinkedIn Parser  │ │
│  │                │  │                │  │                  │ │
│  │ • TF-IDF       │  │ • Profile data │  │ • Profile data   │ │
│  │ • Cosine sim   │  │ • Repositories │  │ • Experience     │ │
│  │ • Skill match  │  │ • Contributions│  │ • Skills         │ │
│  └────────────────┘  └────────────────┘  └──────────────────┘ │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐ │
│  │ Text Extractor │  │ Question Gen   │  │ Leaderboard Gen  │ │
│  │                │  │                │  │                  │ │
│  │ • PDF parse    │  │ • Gemini AI    │  │ • Score combine  │ │
│  │ • DOCX parse   │  │ • Personalize  │  │ • Weighted rank  │ │
│  │ • ZIP extract  │  │ • Format       │  │ • Sort results   │ │
│  └────────────────┘  └────────────────┘  └──────────────────┘ │
│                                                                  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                │ External APIs
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │ GitHub API   │  │ Gemini AI    │  │ Supabase Auth      │   │
│  │              │  │              │  │                    │   │
│  │ Profile data │  │ AI questions │  │ User management    │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow - Resume Ranking

```
1. User Action
   ┌─────────────────────────────────────────┐
   │ User fills form:                        │
   │ • Role: "Backend Developer"             │
   │ • Skills: "Python, Django"              │
   │ • Uploads: resumes.zip                  │
   └────────────┬────────────────────────────┘
                │
                ▼
2. Frontend Processing
   ┌─────────────────────────────────────────┐
   │ JavaScript collects form data           │
   │ Creates FormData object                 │
   │ Sends POST to /api/rank                 │
   └────────────┬────────────────────────────┘
                │
                ▼
3. API Receives Request
   ┌─────────────────────────────────────────┐
   │ Flask validates file type               │
   │ Saves uploaded file securely            │
   │ Extracts ZIP contents                   │
   └────────────┬────────────────────────────┘
                │
                ▼
4. Text Extraction
   ┌─────────────────────────────────────────┐
   │ For each resume:                        │
   │ • Extract text (PDF/DOCX)               │
   │ • Parse candidate name                  │
   │ • Clean and normalize text              │
   └────────────┬────────────────────────────┘
                │
                ▼
5. Scoring & Matching
   ┌─────────────────────────────────────────┐
   │ Build job description from requirements │
   │ Calculate TF-IDF vectors                │
   │ Compute cosine similarity               │
   │ Match required skills                   │
   │ Calculate final score (0-100)           │
   └────────────┬────────────────────────────┘
                │
                ▼
6. Ranking
   ┌─────────────────────────────────────────┐
   │ Sort candidates by score (descending)   │
   │ Format results as JSON                  │
   │ Add metadata (count, timestamp)         │
   └────────────┬────────────────────────────┘
                │
                ▼
7. Response
   ┌─────────────────────────────────────────┐
   │ {                                       │
   │   "success": true,                      │
   │   "results": [                          │
   │     {                                   │
   │       "name": "John Doe",               │
   │       "score": 87.5,                    │
   │       "skills": ["Python", "Django"],   │
   │       "note": "Matched 2/2 skills"      │
   │     }                                   │
   │   ]                                     │
   │ }                                       │
   └────────────┬────────────────────────────┘
                │
                ▼
8. Frontend Display
   ┌─────────────────────────────────────────┐
   │ Parse JSON response                     │
   │ Render ranked list with styling         │
   │ Show scores, skills, notes              │
   │ Display #1, #2, #3 rankings             │
   └─────────────────────────────────────────┘
```

## File Structure Map

```
final-web/
│
├── 📄 QUICKSTART.md              ← Start here!
├── 📄 PROJECT_OVERVIEW.md        ← Complete overview
├── 📄 INTEGRATION_GUIDE.md       ← Frontend integration
│
├── 🔧 backend/
│   ├── 🐍 api.py                 ← Main API server (750+ lines)
│   ├── 📦 requirements.txt       ← All dependencies
│   ├── 🚀 start.sh               ← One-click startup
│   ├── 📖 README.md              ← API documentation
│   ├── 🔐 .env.example           ← Config template
│   │
│   ├── 📂 github-data-fetch/     ← GitHub analysis
│   │   ├── data_fetcher.py       (API calls)
│   │   ├── analyzer.py           (Profile analysis)
│   │   └── matcher.py            (Job matching)
│   │
│   ├── 📂 ibhanwork/             ← Resume processing
│   │   ├── scorematcher.py       (TF-IDF scoring)
│   │   ├── qngenerator.py        (AI questions)
│   │   └── textxtract.py         (Document parsing)
│   │
│   ├── 📂 leaderboard/           ← Combined rankings
│   │   ├── leaderboard.py        (Score combination)
│   │   └── data_loader.py        (Data processing)
│   │
│   └── 📂 linkedin-data-fetch/   ← LinkedIn data
│       └── webhook_server.py     (Data receiver)
│
└── 🎨 DEVANGSHU_FRONTEND/
    ├── 📄 supabase-config.js     ← Auth config
    │
    ├── 📂 COMPANY_MAIN_PAGE/     ← Main application
    │   ├── index.html            (Job posting UI)
    │   ├── script.js             (✨ Updated for API)
    │   └── style.css             (Beautiful design)
    │
    ├── 📂 COMPANY_LOGIN/         ← Login page
    ├── 📂 COMPANY_REGISTRATION/  ← Signup page
    └── 📂 HIRESIGHT_HOME_PAGE/   ← Landing page
```

## Technology Stack Visual

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT SIDE                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  HTML5 + CSS3 + Vanilla JavaScript                         │
│  ├── No framework dependencies                             │
│  ├── Modern ES6+ features                                  │
│  └── Responsive design                                     │
│                                                             │
│  Supabase JavaScript Client                                │
│  └── Authentication & user management                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        SERVER SIDE                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Python 3.8+ Runtime                                       │
│                                                             │
│  Flask Web Framework                                       │
│  ├── Routing and request handling                         │
│  ├── CORS support (flask-cors)                            │
│  └── File upload handling (werkzeug)                      │
│                                                             │
│  Machine Learning                                          │
│  ├── scikit-learn (TF-IDF, cosine similarity)            │
│  ├── numpy (numerical operations)                         │
│  └── pandas (data manipulation)                           │
│                                                             │
│  Document Processing                                       │
│  ├── pdfplumber (PDF extraction)                          │
│  ├── PyPDF2 (PDF fallback)                               │
│  ├── python-docx (DOCX processing)                        │
│  └── zipfile (ZIP handling, built-in)                     │
│                                                             │
│  Text Processing                                           │
│  ├── textblob (NLP utilities)                            │
│  ├── beautifulsoup4 (HTML parsing)                        │
│  └── html2text (HTML to text)                            │
│                                                             │
│  API Integrations                                          │
│  ├── PyGithub (GitHub API)                               │
│  ├── requests (HTTP client)                               │
│  └── External: Gemini AI, Supabase                       │
│                                                             │
│  Utilities                                                 │
│  ├── python-dateutil (date parsing)                       │
│  ├── PyYAML & toml (config files)                        │
│  └── tqdm (progress bars)                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Security & Performance

```
┌───────────────────────────────────────────────────────────┐
│                     SECURITY LAYERS                       │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Input Validation                                        │
│  ├── File type checking (whitelist)                     │
│  ├── File size limits (50MB default)                    │
│  ├── Filename sanitization (secure_filename)            │
│  └── Request validation                                 │
│                                                           │
│  File Handling                                           │
│  ├── Temporary storage                                   │
│  ├── Automatic cleanup after processing                 │
│  └── Secure path handling (no traversal)                │
│                                                           │
│  CORS Configuration                                      │
│  ├── Enabled for development                            │
│  └── Configurable origins for production                │
│                                                           │
│  Error Handling                                          │
│  ├── Graceful failure modes                             │
│  ├── No sensitive data in errors                        │
│  └── Proper HTTP status codes                           │
│                                                           │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│                  PERFORMANCE FEATURES                     │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Efficient Processing                                    │
│  ├── In-memory text extraction                          │
│  ├── Vectorized similarity calculations                 │
│  ├── Batch processing for multiple resumes              │
│  └── Minimal database overhead                          │
│                                                           │
│  Optimization Opportunities                              │
│  ├── Redis caching (future)                            │
│  ├── Celery async processing (future)                   │
│  ├── Database for persistence (future)                  │
│  └── CDN for static assets (future)                     │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION DEPLOYMENT                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Frontend (Static Files)                                   │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ CDN (Netlify/Vercel/CloudFront)                     │  │
│  │ ├── HTML, CSS, JS files                             │  │
│  │ ├── Global distribution                             │  │
│  │ └── HTTPS enabled                                   │  │
│  └─────────────────────────────────────────────────────┘  │
│                            │                                │
│                            │ HTTPS                          │
│                            ▼                                │
│  Load Balancer / Reverse Proxy                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Nginx / CloudFlare                                   │  │
│  │ ├── SSL termination                                 │  │
│  │ ├── Rate limiting                                   │  │
│  │ └── Request routing                                 │  │
│  └─────────────────────────────────────────────────────┘  │
│                            │                                │
│                            ▼                                │
│  Backend API Servers                                       │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Gunicorn + Flask                                     │  │
│  │ ├── Multiple worker processes                       │  │
│  │ ├── Auto-scaling enabled                            │  │
│  │ └── Health checks                                   │  │
│  └─────────────────────────────────────────────────────┘  │
│                            │                                │
│                            ▼                                │
│  External Services                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐  │
│  │ GitHub API  │  │ Gemini AI   │  │ Supabase         │  │
│  └─────────────┘  └─────────────┘  └──────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
