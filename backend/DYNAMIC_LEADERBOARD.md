# Dynamic Leaderboard System - Implementation Guide

## 🎯 Overview

The Dynamic Leaderboard System enables real-time generation of candidate leaderboards from uploaded resumes. It combines:
- **LinkedIn-style scores** (resume-job description similarity)
- **GitHub profile analysis** (developer metrics and skills)
- **Session-based storage** (isolated data per job posting)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    UPLOAD & PROCESSING FLOW                      │
└─────────────────────────────────────────────────────────────────┘

1. Company uploads ZIP/PDFs → /api/rank-with-leaderboard
                ↓
2. Create Session (session_company_job_timestamp)
                ↓
3. Extract & Process Resumes
                ↓
        ┌───────────────────────────────┐
        │   PARALLEL PROCESSING         │
        ├───────────────────────────────┤
        │                               │
        │  A) LinkedIn Scores           │  B) GitHub Analysis
        │     • TF-IDF vectorization    │     • Extract usernames
        │     • Cosine similarity       │     • Fetch profile data
        │     • Save results.csv        │     • Analyze repos
        │                               │     • Save analysis_*.json
        │                               │
        └───────────────────────────────┘
                ↓
4. Generate Leaderboard
    • Load results.csv
    • Load analysis_*.json files
    • Normalize scores (0-1 scale)
    • Calculate weighted average
    • Rank candidates
                ↓
5. Return: { session_id, leaderboard, ranked_candidates }
```

## 📁 Directory Structure

```
uploads/
├── session_acme_dev001_20251030_143022/
│   ├── metadata.json                    # Session info
│   ├── results.csv                      # LinkedIn scores
│   ├── leaderboard.json                 # Generated leaderboard
│   ├── resumes/                         # Extracted resume files
│   │   ├── john_doe.pdf
│   │   └── jane_smith.pdf
│   └── reports/                         # GitHub analyses
│       ├── analysis_johndoe.json
│       └── analysis_janesmith.json
├── session_techcorp_backend_20251030_150000/
│   └── ...
```

## 🔧 Components

### 1. Session Manager (`utils/session_manager.py`)

Manages isolated storage for each job posting.

**Key Methods:**
- `create_session()` - Create new session with unique ID
- `get_session_dir()` - Get path to session directory
- `get_session_metadata()` - Load session metadata
- `update_session_metadata()` - Update session info
- `list_sessions()` - List all sessions
- `cleanup_old_sessions()` - Remove old sessions
- `delete_session()` - Delete specific session

**Session ID Format:**
```
session_<company_id>_<job_id>_<timestamp>
Example: session_acme_dev001_20251030_143022
```

### 2. LinkedIn Score Generator (`utils/linkedin_score_generator.py`)

Calculates resume-job description similarity.

**Process:**
1. Build job description from requirements
2. Vectorize using TF-IDF (max 500 features, bigrams)
3. Calculate cosine similarity for each resume
4. Output results.csv in format:
   ```csv
   Candidate,Score
   John Doe,0.8542
   Jane Smith,0.7321
   ```

**Key Methods:**
- `calculate_similarity_score()` - Single resume vs job description
- `generate_scores_for_candidates()` - Batch processing
- `build_job_description_from_requirements()` - Format job description

### 3. GitHub Analysis Generator (`utils/github_analysis_generator.py`)

Extracts GitHub usernames and analyzes profiles.

**Process:**
1. Extract GitHub username using regex patterns:
   - `github.com/username`
   - `GitHub: @username`
2. Call GitHubService to analyze profile
3. Transform to leaderboard format
4. Save as `analysis_<username>.json`

**Analysis JSON Format:**
```json
{
  "username": "johndoe",
  "analysis_date": "2025-10-30T14:30:22",
  "profile": {
    "name": "John Doe",
    "bio": "Backend Developer",
    "followers": 150,
    "public_repos": 45
  },
  "metrics": {
    "overall_score": 85.5,
    "total_repos": 45,
    "total_stars": 230,
    "languages": {"Python": 45, "JavaScript": 30},
    "activity_score": 78,
    "quality_score": 82
  },
  "skills_matched": ["Python", "Django", "Docker"]
}
```

### 4. Dynamic Leaderboard Generator (`utils/dynamic_leaderboard.py`)

Generates leaderboards from session data.

**Process:**
1. Load results.csv (LinkedIn scores 0-1)
2. Load analysis_*.json files (GitHub scores 0-100)
3. Normalize GitHub scores to 0-1 scale
4. Calculate weighted combined score:
   ```python
   combined = (linkedin * linkedin_weight) + (github/100 * github_weight)
   ```
5. Rank by combined score
6. Classify into tiers (Excellent, Very Good, etc.)

**Tier Classification:**
- 🌟 Excellent: 80-100%
- ⭐ Very Good: 70-80%
- ✨ Good: 60-70%
- 💫 Fair: 50-60%
- ⚡ Moderate: 40-50%
- 🔸 Low: <40%

## 🌐 API Endpoints

### POST /api/rank-with-leaderboard
**Enhanced endpoint with full pipeline**

**Request:**
```bash
curl -X POST http://localhost:5000/api/rank-with-leaderboard \
  -F "company_id=acme" \
  -F "job_id=dev001" \
  -F "job_title=Backend Developer" \
  -F "role=Backend Developer" \
  -F "skills=Python, Django, PostgreSQL" \
  -F "experience=3+ years" \
  -F "file=@resumes.zip" \
  -F "generate_github=true" \
  -F "linkedin_weight=0.5" \
  -F "github_weight=0.5"
```

**Response:**
```json
{
  "success": true,
  "session_id": "session_acme_dev001_20251030_143022",
  "results": [...],
  "count": 15,
  "leaderboard": [
    {
      "rank": 1,
      "name": "John Doe",
      "combined_score": 0.8567,
      "linkedin_score": 0.8542,
      "github_score": 0.8592,
      "tier": "Excellent Match",
      "emoji": "🌟"
    }
  ],
  "leaderboard_statistics": {
    "mean": 0.6734,
    "median": 0.6520,
    "min": 0.4215,
    "max": 0.8967
  },
  "message": "Session created successfully. Access full leaderboard at /api/leaderboard/session_acme_dev001_20251030_143022"
}
```

### GET /api/leaderboard/:session_id
**Get leaderboard for a session**

**Request:**
```bash
curl http://localhost:5000/api/leaderboard/session_acme_dev001_20251030_143022?top_n=20
```

**Query Parameters:**
- `linkedin_weight` (float, default: 0.5) - Weight for LinkedIn scores
- `github_weight` (float, default: 0.5) - Weight for GitHub scores
- `min_score` (float, default: 0.0) - Minimum score threshold
- `top_n` (int, default: 20) - Number of top candidates

**Response:**
```json
{
  "success": true,
  "session_id": "session_acme_dev001_20251030_143022",
  "leaderboard": [...],
  "total_candidates": 15,
  "top_n": 20,
  "statistics": {...},
  "weights": {
    "linkedin": 0.5,
    "github": 0.5
  }
}
```

### GET /api/session/:session_id
**Get session information**

**Response:**
```json
{
  "success": true,
  "session_id": "session_acme_dev001_20251030_143022",
  "metadata": {
    "company_id": "acme",
    "job_id": "dev001",
    "job_title": "Backend Developer",
    "created_at": "2025-10-30T14:30:22",
    "status": "completed",
    "candidates_processed": 15
  },
  "files": {
    "results_csv": true,
    "reports_dir": true,
    "leaderboard_json": true,
    "github_analyses_count": 12
  }
}
```

### GET /api/sessions
**List all sessions**

**Query Parameters:**
- `company_id` (string, optional) - Filter by company
- `limit` (int, optional) - Max sessions to return

### DELETE /api/session/:session_id
**Delete a session**

### POST /api/sessions/cleanup
**Cleanup old sessions**

**Request:**
```json
{
  "days": 7,
  "dry_run": false
}
```

### GET /api/sessions/stats
**Get storage statistics**

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_sessions": 23,
    "total_size_bytes": 156789123,
    "total_size_mb": 149.53,
    "base_directory": "/path/to/uploads"
  }
}
```

## 📊 Score Calculation

### LinkedIn Score (Resume Similarity)
```python
# TF-IDF Vectorization
vectorizer = TfidfVectorizer(
    max_features=500,
    stop_words='english',
    ngram_range=(1, 2),
    min_df=1
)

# Cosine Similarity
score = cosine_similarity(job_vector, resume_vector)[0][0]
# Output: 0.0 - 1.0
```

### GitHub Score (Profile Analysis)
```python
# Components:
activity_score = contributions + commit frequency
quality_score = code quality + documentation
popularity_score = stars + followers

# Combined (0-100 scale)
overall_score = weighted_average(activity, quality, popularity)
```

### Combined Leaderboard Score
```python
# Normalize GitHub to 0-1 scale
github_normalized = github_score / 100

# Weighted average (default 50/50)
combined = (linkedin * 0.5) + (github_normalized * 0.5)

# Result: 0.0 - 1.0
```

## 🔄 Workflow Example

### Backend Integration
```python
# In your API handler
from utils.session_manager import create_session_manager
from utils.linkedin_score_generator import generate_linkedin_scores
from utils.github_analysis_generator import generate_github_analyses
from utils.dynamic_leaderboard import generate_leaderboard_for_session

# 1. Create session
session_mgr = create_session_manager(UPLOAD_FOLDER)
session_id, session_dir = session_mgr.create_session(
    company_id=company_id,
    job_id=job_id,
    job_title=job_title
)

# 2. Process uploads and extract candidates
candidates = [...]  # Your existing resume processing

# 3. Generate LinkedIn scores
linkedin_result = generate_linkedin_scores(
    candidates, job_requirements, session_dir
)

# 4. Generate GitHub analyses
github_result = generate_github_analyses(
    candidates, job_requirements, session_dir
)

# 5. Generate leaderboard
leaderboard = generate_leaderboard_for_session(
    session_dir,
    linkedin_weight=0.5,
    github_weight=0.5
)

# 6. Return session_id
return {
    'session_id': session_id,
    'leaderboard': leaderboard['leaderboard']
}
```

### Frontend Integration
```javascript
// 1. Upload resumes
const formData = new FormData();
formData.append('file', zipFile);
formData.append('company_id', 'acme');
formData.append('job_id', 'dev001');
formData.append('role', 'Backend Developer');
formData.append('skills', 'Python, Django');

const response = await fetch('/api/rank-with-leaderboard', {
  method: 'POST',
  body: formData
});

const result = await response.json();
const sessionId = result.session_id;

// 2. Display initial leaderboard
displayLeaderboard(result.leaderboard);

// 3. Later, fetch updated leaderboard with custom weights
const leaderboard = await fetch(
  `/api/leaderboard/${sessionId}?linkedin_weight=0.6&github_weight=0.4&top_n=50`
);
```

## 🎨 Customization

### Adjust Score Weights
```python
# LinkedIn-heavy (60/40)
leaderboard = generate_leaderboard_for_session(
    session_dir,
    linkedin_weight=0.6,
    github_weight=0.4
)

# GitHub-heavy (30/70)
leaderboard = generate_leaderboard_for_session(
    session_dir,
    linkedin_weight=0.3,
    github_weight=0.7
)
```

### Filter by Minimum Score
```python
# Only candidates with 70%+ combined score
leaderboard = generate_leaderboard_for_session(
    session_dir,
    min_score=0.7
)
```

### Custom TF-IDF Parameters
```python
# In linkedin_score_generator.py
vectorizer = TfidfVectorizer(
    max_features=1000,  # More features
    stop_words='english',
    ngram_range=(1, 3),  # Include trigrams
    min_df=2  # Require terms in at least 2 docs
)
```

## 🧹 Maintenance

### Automated Cleanup (Cron Job)
```bash
# Cleanup sessions older than 7 days (daily at 2 AM)
0 2 * * * curl -X POST http://localhost:5000/api/sessions/cleanup \
  -H "Content-Type: application/json" \
  -d '{"days": 7, "dry_run": false}'
```

### Manual Cleanup
```python
from utils.session_manager import create_session_manager

session_mgr = create_session_manager('/uploads')

# Preview what would be deleted
deleted = session_mgr.cleanup_old_sessions(days=7, dry_run=True)
print(f"Would delete: {deleted}")

# Actually delete
deleted = session_mgr.cleanup_old_sessions(days=7, dry_run=False)
print(f"Deleted: {deleted}")
```

### Storage Monitoring
```python
stats = session_mgr.get_storage_stats()
print(f"Total sessions: {stats['total_sessions']}")
print(f"Storage used: {stats['total_size_mb']} MB")
```

## 🐛 Troubleshooting

### Issue: GitHub analysis not working
**Solution:** Ensure GITHUB_TOKEN environment variable is set:
```bash
export GITHUB_TOKEN=your_github_token
```

### Issue: Empty leaderboard
**Causes:**
1. No results.csv or analysis_*.json files
2. All scores below min_score threshold
3. Invalid session_id

**Debug:**
```bash
# Check session files
curl http://localhost:5000/api/session/YOUR_SESSION_ID

# Check storage stats
curl http://localhost:5000/api/sessions/stats
```

### Issue: Low GitHub analysis success rate
**Causes:**
1. GitHub usernames not found in resumes
2. Rate limiting (GitHub API)
3. Private profiles

**Solutions:**
- Ask candidates to include GitHub URLs prominently
- Use authenticated API requests with token
- Set `skip_on_error=True` to continue processing

## 📈 Performance Tips

1. **Batch Processing:** Process multiple resumes in parallel
2. **Caching:** Cache GitHub analyses for common usernames
3. **Async Processing:** Use background tasks for large uploads
4. **Storage Limits:** Set max session age and size limits
5. **Rate Limiting:** Respect GitHub API rate limits

## 🔒 Security Considerations

1. **File Validation:** Only allow specified file types
2. **ZIP Bomb Protection:** Limit extracted file sizes
3. **Directory Traversal:** Sanitize file paths
4. **API Rate Limiting:** Prevent abuse
5. **Session Isolation:** Ensure data privacy per company/job

## 📚 Further Reading

- [Leaderboard Module Documentation](../leaderboard/README.md)
- [GitHub Service Documentation](../services/README.md)
- [API Integration Guide](../INTEGRATION_GUIDE.md)
