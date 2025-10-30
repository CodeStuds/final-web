# Backend Utilities

This directory contains organized utility modules for the HireSight backend:

## Core Modules

### contact_extractor.py
Extracts contact information from resume text including:
- Email addresses
- Phone numbers
- LinkedIn URLs
- GitHub URLs

**Usage:**
```python
from utils.contact_extractor import extract_contacts

contacts = extract_contacts(resume_text)
print(contacts['emails'])  # List of email addresses
print(contacts['linkedin'])  # List of LinkedIn URLs
```

### resume_text_extractor.py
Extracts text from various resume file formats:
- PDF (using pdfplumber and PyPDF2)
- DOCX (using python-docx)
- TXT (plain text)

**Usage:**
```python
from utils.resume_text_extractor import extract_resume_text

text = extract_resume_text('path/to/resume.pdf')
print(text)
```

### resume_scorer.py
Scores and ranks resumes against job descriptions using TF-IDF and cosine similarity.

**Usage:**
```python
from utils.resume_scorer import ResumeScorer

scorer = ResumeScorer()
results = scorer.score_resumes(job_description, resumes)
for result in results:
    print(f"{result['name']}: {result['score']}")
```

## Dynamic Leaderboard System

### session_manager.py
Manages upload sessions for job postings with isolated storage.

**Features:**
- Creates unique session IDs for each job posting
- Isolated storage for resumes, scores, and analyses
- Session metadata management
- Automatic cleanup of old sessions
- Storage statistics

**Usage:**
```python
from utils.session_manager import create_session_manager

session_mgr = create_session_manager('/path/to/uploads')
session_id, session_dir = session_mgr.create_session(
    company_id='acme',
    job_id='dev001',
    job_title='Backend Developer'
)
```

### linkedin_score_generator.py
Generates LinkedIn-style resume similarity scores and creates results.csv files.

**Features:**
- Calculates cosine similarity between resumes and job descriptions
- Outputs results.csv compatible with leaderboard system
- TF-IDF vectorization with configurable parameters
- Automatic score normalization (0-1 scale)

**Usage:**
```python
from utils.linkedin_score_generator import generate_linkedin_scores

job_requirements = {
    'role': 'Backend Developer',
    'skills': 'Python, Django, PostgreSQL',
    'experience': '3+ years'
}

candidates = [
    {'name': 'John Doe', 'text': 'resume text...'},
    {'name': 'Jane Smith', 'text': 'resume text...'}
]

result = generate_linkedin_scores(candidates, job_requirements, session_dir)
print(result['csv_path'])  # Path to generated results.csv
```

### github_analysis_generator.py
Extracts GitHub usernames from resumes and generates analysis JSON files.

**Features:**
- Extracts GitHub usernames using regex patterns
- Analyzes GitHub profiles using GitHubService
- Generates analysis_*.json files in leaderboard format
- Handles missing GitHub profiles gracefully
- Parallel processing support

**Usage:**
```python
from utils.github_analysis_generator import generate_github_analyses

job_requirements = {
    'role': 'Backend Developer',
    'required_skills': ['Python', 'Django']
}

candidates = [
    {'name': 'John Doe', 'text': 'github.com/johndoe resume text...'},
    {'name': 'Jane Smith', 'text': 'github.com/janesmith resume text...'}
]

result = generate_github_analyses(candidates, job_requirements, session_dir)
print(f"Generated: {result['analyses_generated']}")
print(f"Skipped: {result['analyses_skipped']}")
```

### dynamic_leaderboard.py
Generates leaderboards from session-specific data files.

**Features:**
- Loads results.csv and analysis_*.json from session directory
- Calculates weighted combined scores
- Ranks candidates by combined score
- Configurable weights and thresholds
- JSON output with statistics

**Usage:**
```python
from utils.dynamic_leaderboard import generate_leaderboard_for_session

leaderboard = generate_leaderboard_for_session(
    session_dir='/path/to/session',
    linkedin_weight=0.5,
    github_weight=0.5,
    min_score=0.0,
    top_n=20
)

print(f"Total candidates: {leaderboard['total_candidates']}")
for candidate in leaderboard['leaderboard']:
    print(f"{candidate['rank']}. {candidate['name']}: {candidate['combined_score']}")
```

## Complete Workflow Example

```python
from utils.session_manager import create_session_manager
from utils.linkedin_score_generator import generate_linkedin_scores
from utils.github_analysis_generator import generate_github_analyses
from utils.dynamic_leaderboard import generate_leaderboard_for_session

# 1. Create session
session_mgr = create_session_manager('/uploads')
session_id, session_dir = session_mgr.create_session(
    company_id='acme',
    job_id='backend-001',
    job_title='Backend Developer'
)

# 2. Process resumes (your existing code)
candidates = [...]  # Extract from uploaded files

# 3. Generate LinkedIn scores
job_requirements = {'role': 'Backend Developer', 'skills': 'Python, Django'}
linkedin_result = generate_linkedin_scores(candidates, job_requirements, session_dir)

# 4. Generate GitHub analyses
github_result = generate_github_analyses(candidates, job_requirements, session_dir)

# 5. Generate leaderboard
leaderboard = generate_leaderboard_for_session(session_dir, top_n=20)

# 6. Return session_id to frontend
return {'session_id': session_id, 'leaderboard': leaderboard['leaderboard']}
```

## Original Scripts

These utilities were converted from the following original Colab scripts in `backend/ibhanwork/`:

- `emailextractor.py` → `contact_extractor.py`
- `textxtract.py` → `resume_text_extractor.py`
- `scorematcher.py` → `resume_scorer.py`
- `qngenerator.py` → Functionality integrated into `services/interview_service.py`

## Dependencies

- **contact_extractor**: No external dependencies (uses re module)
- **resume_text_extractor**: PyPDF2, pdfplumber, python-docx
- **resume_scorer**: scikit-learn

Install dependencies:
```bash
pip install PyPDF2 pdfplumber python-docx scikit-learn
```
