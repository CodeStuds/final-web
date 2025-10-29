# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**HireSight** is a comprehensive hiring platform that combines LinkedIn resume analysis, GitHub profile evaluation, and frontend interfaces for candidates and companies. The project consists of four main backend services and multiple frontend pages.

## Repository Structure

```
final-web/
├── backend/
│   ├── github-data-fetch/    # GitHub profile analysis (HireSight core)
│   ├── linkedin-data-fetch/  # LinkedIn scraper browser extension
│   ├── ibhanwork/             # Resume-job description matching
│   └── leaderboard/           # Unified candidate ranking system
└── DEVANGSHU_FRONTEND/        # Static HTML/CSS/JS frontend pages
    ├── HIRESIGHT_HOME_PAGE/
    ├── CANDIDATE_SIGNUP/
    ├── COMPANY_LOGIN/
    ├── COMPANY_REGISTRATION/
    └── COMPANY_MAIN_PAGE/
```

## Backend Services

### 1. GitHub Data Fetch (github-data-fetch/)

Performs comprehensive GitHub profile analysis using a 4-factor matching algorithm.

**Key Files:**
- `main.py`: Entry point and CLI orchestration
- `data_fetcher.py`: GitHub API wrapper (PyGithub)
- `analyzer.py`: Core analysis engine with 6 analysis dimensions
- `matcher.py`: 4-factor matching algorithm (Current Fit 40%, Growth Potential 30%, Collaboration 20%, Code Quality 10%)
- `output_generator.py`: JSON and Markdown report generation
- `config.py`: 100+ technology mappings and scoring weights
- `utils.py`: CacheManager, date calculations, conventional commit detection

**Setup:**
```bash
cd backend/github-data-fetch
pip install -r requirements.txt
python -m textblob.download_corpora
export GITHUB_TOKEN="your_github_token"  # Required for API rate limits
```

**Common Commands:**
```bash
# Basic analysis
python main.py <username>

# With job requirements
python main.py <username> --job-title "Backend Developer" \
  --required-skills "Python,Django,PostgreSQL,Docker" \
  --preferred-skills "AWS,Redis,GraphQL"

# Custom work style and output
python main.py <username> --work-style collaborative --output-dir ./reports

# More repos, no cache
python main.py <username> --top-repos 15 --no-cache

# JSON only
python main.py <username> --json-only
```

**Output:**
- `analysis_username.json`: Complete analysis data
- `report_username.md`: Human-readable report with recommendations

### 2. LinkedIn Data Fetch (linkedin-data-fetch/)

Browser extension that scrapes LinkedIn profiles and sends data to a webhook server.

**Key Files:**
- `webhook_server.py`: Flask server that receives scraped data
- `content.js`: Content script for LinkedIn pages
- `background.js`: Background service worker
- `manifest.json`: Chrome/Firefox extension manifest

**Setup:**
```bash
cd backend/linkedin-data-fetch
pip install -r requirements.txt
```

**Run Webhook Server:**
```bash
python webhook_server.py
# Server runs on http://localhost:5000
# Saves scraped profiles to output/<profile>.txt
```

**Browser Extension:**
1. Load unpacked extension from `linkedin-data-fetch/` directory
2. Navigate to LinkedIn profile
3. Click extension icon → "Scrape This Page"
4. Data sent to webhook and saved to `output/` directory

### 3. Resume Matcher (ibhanwork/)

TF-IDF based resume-to-job description matching using cosine similarity.

**Key Files:**
- `scorematcher.py`: Main matching logic (TF-IDF + cosine similarity)
- `textxtract.py`: Text extraction utilities

**Configuration:**
Edit `scorematcher.py` to set:
- `ZIP_PATH`: Path to resumes zip file
- `DESC_PATH`: Path to job description text file
- `EXTRACT_DIR`: Where to extract resumes

**Run:**
```bash
cd backend/ibhanwork
python scorematcher.py
# Outputs: results.csv with Candidate,Score columns (0-1 scale)
```

### 4. Leaderboard System (leaderboard/)

Combines LinkedIn and GitHub scores into a unified ranking.

**Key Files:**
- `main.py`: CLI entry point
- `data_loader.py`: Loads and merges data from both sources
- `leaderboard.py`: Score calculation, ranking, tier classification
- `output_generator.py`: JSON, CSV, and Markdown report generation
- `config.py`: Weights, thresholds, paths

**Setup:**
Requires data from both `ibhanwork` and `github-data-fetch` to already exist:
- LinkedIn: `../ibhanwork/results.csv`
- GitHub: `../github-data-fetch/reports/analysis_USERNAME.json`

**Common Commands:**
```bash
cd backend/leaderboard

# Default (50/50 weight)
python main.py

# Prioritize GitHub scores (60/40)
python main.py --linkedin-weight 0.4 --github-weight 0.6

# Filter by minimum score
python main.py --min-score 0.5 --top 20

# Custom paths
python main.py --linkedin-path /path/to/results.csv \
  --github-path /path/to/reports/ \
  --output-dir ./my_output

# JSON only or console only
python main.py --json-only
python main.py --no-output
```

**Output:**
- `leaderboard.json`: Structured candidate data with scores
- `leaderboard.csv`: Spreadsheet-compatible format
- `leaderboard.md`: Formatted report with tier distribution

**Score Calculation:**
```
combined_score = (linkedin_score × linkedin_weight + github_score × github_weight) /
                 (linkedin_weight + github_weight)
```

**Tier Classification:**
- 0.85-1.00: Excellent Match 🥇
- 0.75-0.84: Very Good Match 🥈
- 0.65-0.74: Good Match 🥉
- 0.50-0.64: Moderate Match ✅
- 0.35-0.49: Fair Match ⚠️
- 0.00-0.34: Low Match ❌

## Frontend

Static HTML/CSS/JS pages using Supabase for authentication.

**Key Files:**
- `supabase-config.js`: Shared Supabase client configuration
- Each directory contains: `index.html`, `style.css`, and page-specific JS

**Pages:**
- `HIRESIGHT_HOME_PAGE/`: Landing page with service overview
- `CANDIDATE_SIGNUP/`: Candidate registration form
- `COMPANY_LOGIN/`: Company authentication
- `COMPANY_REGISTRATION/`: Company signup form
- `COMPANY_MAIN_PAGE/`: Company dashboard

**Supabase Integration:**
All pages import Supabase client from CDN and use shared config:
```javascript
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
```

**No Build Step Required:** Frontend is static files that can be opened directly in a browser.

## Complete Workflow

### For Candidate Evaluation:

1. **Collect GitHub data:**
```bash
cd backend/github-data-fetch
python main.py <candidate_username> --job-title "Role" --required-skills "Skills"
```

2. **Collect LinkedIn data:**
```bash
cd backend/linkedin-data-fetch
python webhook_server.py  # Start server
# Use browser extension to scrape LinkedIn profile
```

3. **Match resumes to job description:**
```bash
cd backend/ibhanwork
# Edit scorematcher.py with paths to resumes.zip and desc.txt
python scorematcher.py
```

4. **Generate unified leaderboard:**
```bash
cd backend/leaderboard
python main.py --github-weight 0.6 --linkedin-weight 0.4 --min-score 0.5
```

## Architecture Notes

### Backend Integration Pattern

The system uses a **pipeline architecture** where each service produces output consumed by downstream services:

```
LinkedIn Scraper → output/*.txt
Resume Matcher → results.csv → Leaderboard
GitHub Analyzer → analysis_*.json → Leaderboard
```

**Data Flow:**
- LinkedIn scraper: Standalone, outputs text files
- Resume matcher: Produces CSV with candidate names and similarity scores (0-1)
- GitHub analyzer: Produces JSON per candidate with comprehensive analysis (0-100)
- Leaderboard: Consumes both CSV and JSON files, normalizes scores, ranks candidates

### Key Design Patterns

1. **Modular Services:** Each backend service is independent and can run standalone
2. **File-based Integration:** Services communicate via files (CSV, JSON, TXT)
3. **Score Normalization:** Leaderboard normalizes different scales (0-1 and 0-100)
4. **Evidence-based Scoring:** GitHub analyzer uses quantifiable metrics (LOC, commits, PRs)
5. **Weighted Averaging:** Leaderboard allows configurable weights for different signals

### GitHub Analyzer Architecture

The most complex service follows a **pipeline pattern**:
```
CLI Input → Data Fetcher → Analyzer → Matcher → Output Generator
```

**Analysis Dimensions:**
1. Skills (100+ technologies with confidence scoring 0-100)
2. Contribution patterns (commit frequency, PR activity, code reviews)
3. Work style classification (Solo/Collaborative/Mentorship/Async-Friendly)
4. Code quality (documentation, testing, maintenance)
5. Learning trajectory (skill acquisition, growth velocity)
6. Job matching (4-factor algorithm with bias detection)

**Scoring Formula (Skill Confidence):**
```
confidence = (lines_of_code/max_loc)*20 + (repo_count/max_repos)*30 +
             recency_score*30 + (complexity/max_complexity)*20
```

**Matching Weights:**
- Current Fit: 40% (direct skill overlap)
- Growth Potential: 30% (learning ability)
- Collaboration Fit: 20% (work style compatibility)
- Code Quality: 10% (standards and practices)

### Caching Strategy

GitHub analyzer uses file-based caching (`.cache/` directory, 24hr lifetime) to minimize API calls. Use `--no-cache` to force fresh data.

## Common Development Tasks

### Adding New Technology Mappings

Edit `backend/github-data-fetch/config.py` in the `DEPENDENCY_MAPPINGS` dictionary:
```python
DEPENDENCY_MAPPINGS = {
    'your-framework': {
        'type': 'framework',
        'category': 'Backend',
        'name': 'Your Framework'
    }
}
```

### Customizing Matching Weights

Edit `backend/github-data-fetch/config.py`:
```python
MATCHING_WEIGHTS = {
    'current_fit': 0.40,
    'growth_potential': 0.30,
    'collaboration_fit': 0.20,
    'code_quality': 0.10,
}
```

Or edit `backend/leaderboard/config.py`:
```python
LINKEDIN_WEIGHT = 0.5
GITHUB_WEIGHT = 0.5
```

### Adding New Analysis Modules

1. Add function to `backend/github-data-fetch/analyzer.py`
2. Update `perform_complete_analysis()` to call your function
3. Add output formatting in `output_generator.py`

### Extending Report Formats

Add new format function in `backend/github-data-fetch/output_generator.py` or `backend/leaderboard/output_generator.py`.

## Environment Requirements

**Python:** 3.10+ (for github-data-fetch), 3.7+ (for others)

**Backend Dependencies:**
- PyGithub: GitHub API wrapper
- Flask: Webhook server
- scikit-learn: TF-IDF and cosine similarity
- TextBlob: Sentiment analysis (requires corpora download)
- BeautifulSoup4: HTML parsing
- pandas, numpy: Data manipulation

**Frontend:**
- No build tools required
- Supabase JS SDK via CDN
- Modern browser with ES6 support

## Troubleshooting

### GitHub API Rate Limits
Set `GITHUB_TOKEN` environment variable (increases limit from 60 to 5000 requests/hour)

### TextBlob Corpora Missing
```bash
python -m textblob.download_corpora
```

### No Candidates in Leaderboard
- Verify `results.csv` exists in `ibhanwork/`
- Verify `analysis_*.json` files exist in `github-data-fetch/reports/`
- Check that candidate names match between sources

### LinkedIn Extension Not Working
- Ensure you're on a LinkedIn page (*.linkedin.com)
- Verify webhook server is running on localhost:5000
- Check browser console for errors (F12)

### Missing Python Dependencies
```bash
pip install -r requirements.txt
```
