#!/usr/bin/env python3
"""
HireSight Unified API
A comprehensive Flask API that integrates all backend components:
- Resume scoring and candidate ranking
- GitHub profile analysis
- LinkedIn data processing
- Leaderboard generation
- Interview question generation
"""

import os
import sys
import json
import tempfile
import shutil
import zipfile
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hiresight.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add backend subdirectories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'github-data-fetch'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ibhanwork'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'leaderboard'))
sys.path.insert(0, os.path.dirname(__file__))  # For candidate_scorer

# Import backend modules
try:
    from github_data_fetch.data_fetcher import GitHubDataFetcher
    from github_data_fetch.analyzer import GitHubAnalyzer
    from github_data_fetch.matcher import CandidateMatcher
except ImportError:
    # Fallback for direct imports
    try:
        from data_fetcher import GitHubDataFetcher
        from analyzer import GitHubAnalyzer
        from matcher import CandidateMatcher
    except ImportError:
        logger.warning("GitHub modules not available")
        GitHubDataFetcher = None
        GitHubAnalyzer = None
        CandidateMatcher = None

# Import unified candidate scorer
try:
    from candidate_scorer import CandidateScorer, CompatibilityScorer
except ImportError:
    logger.warning("Candidate scorer module not available")
    CandidateScorer = None
    CompatibilityScorer = None

# Import resume URL extractor
try:
    from resume_url_extractor import ResumeURLExtractor, extract_github_username, extract_linkedin_profile
except ImportError:
    logger.warning("Resume URL extractor module not available")
    ResumeURLExtractor = None
    extract_github_username = None
    extract_linkedin_profile = None


# Configuration
# Set up Flask to serve frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'DEVANGSHU_FRONTEND')
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)  # Enable CORS for frontend communication

# Setup rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour", "20 per minute"],
    storage_uri="memory://"
)

# API Key configuration (optional, for production)
API_KEYS_ENABLED = os.environ.get('API_KEYS_ENABLED', 'False').lower() == 'true'
VALID_API_KEYS = set(os.environ.get('API_KEYS', '').split(',')) if os.environ.get('API_KEYS') else set()

# File upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'zip', 'pdf', 'docx', 'doc', 'txt'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_ZIP_EXTRACTED_SIZE = 200 * 1024 * 1024  # 200MB max extracted size (ZIP bomb protection)
MAX_ZIP_FILES = 100  # Maximum number of files in a ZIP

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def require_api_key(f):
    """
    Decorator to require API key authentication

    Checks for API key in:
    1. X-API-Key header
    2. api_key query parameter

    Only enforced if API_KEYS_ENABLED environment variable is set to True
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not API_KEYS_ENABLED:
            # API key authentication is disabled
            return f(*args, **kwargs)

        # Check header first
        api_key = request.headers.get('X-API-Key')

        # Fall back to query parameter
        if not api_key:
            api_key = request.args.get('api_key')

        # Validate API key
        if not api_key or api_key not in VALID_API_KEYS:
            logger.warning(f"Unauthorized API access attempt from {get_remote_address()}")
            return jsonify({
                'error': 'Invalid or missing API key',
                'message': 'Provide a valid API key via X-API-Key header or api_key parameter'
            }), 401

        return f(*args, **kwargs)

    return decorated_function


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_safe_path(base_path: str, target_path: str) -> bool:
    """
    Check if target_path is safely within base_path (prevents directory traversal)

    Args:
        base_path: The base directory that should contain the file
        target_path: The target file path to validate

    Returns:
        bool: True if path is safe, False otherwise
    """
    # Resolve to absolute paths
    base = os.path.abspath(base_path)
    target = os.path.abspath(target_path)

    # Ensure target is within base directory
    return target.startswith(base)


def safe_extract_zip(zip_path: str, extract_dir: str) -> tuple[bool, str]:
    """
    Safely extract ZIP file with protection against ZIP bombs and directory traversal

    Args:
        zip_path: Path to ZIP file
        extract_dir: Directory to extract files to

    Returns:
        tuple: (success: bool, error_message: str)
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Check total extracted size and file count
            total_size = 0
            file_count = 0

            for info in zip_ref.infolist():
                file_count += 1
                total_size += info.file_size

                # Check limits
                if file_count > MAX_ZIP_FILES:
                    return False, f"ZIP contains too many files (max {MAX_ZIP_FILES})"

                if total_size > MAX_ZIP_EXTRACTED_SIZE:
                    return False, f"ZIP extracted size too large (max {MAX_ZIP_EXTRACTED_SIZE / (1024*1024):.0f}MB)"

                # Check for directory traversal
                extract_path = os.path.join(extract_dir, info.filename)
                if not is_safe_path(extract_dir, extract_path):
                    return False, f"ZIP contains unsafe path: {info.filename}"

            # Extract if all checks pass
            zip_ref.extractall(extract_dir)
            return True, ""

    except zipfile.BadZipFile:
        return False, "Invalid or corrupted ZIP file"
    except Exception as e:
        return False, f"ZIP extraction error: {str(e)}"


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF files"""
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except ImportError:
        # Fallback to PyPDF2
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}", exc_info=True)
            return ""


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX files"""
    try:
        from docx import Document
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting DOCX: {e}", exc_info=True)
        return ""


def extract_text_from_file(file_path: str) -> str:
    """Extract text from various file formats"""
    ext = file_path.rsplit('.', 1)[1].lower() if '.' in file_path else ''
    
    if ext == 'pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['docx', 'doc']:
        return extract_text_from_docx(file_path)
    elif ext == 'txt':
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    else:
        return ""


def score_candidate_resume(resume_text: str, job_requirements: Dict[str, Any]) -> Dict[str, Any]:
    """
    Score a single candidate's resume against job requirements
    Uses TF-IDF similarity scoring
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    
    # Build job description from requirements
    job_desc = f"""
    Role: {job_requirements.get('role', '')}
    Required Skills: {job_requirements.get('skills', '')}
    Experience Required: {job_requirements.get('experience', 'Not specified')}
    CGPA Required: {job_requirements.get('cgpa', 'Not specified')}
    Additional Requirements: {job_requirements.get('additional', '')}
    """
    
    # Calculate similarity score
    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        tfidf_matrix = vectorizer.fit_transform([job_desc, resume_text])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        score = round(similarity * 100, 2)
    except Exception as e:
        logger.error(f"Error calculating score: {e}", exc_info=True)
        score = 50.0  # Default score
    
    return {
        'score': score,
        'similarity': similarity if 'similarity' in locals() else 0.5
    }


def validate_job_requirements(data: dict) -> tuple[bool, Optional[str]]:
    """
    Validate job requirements input

    Args:
        data: Dictionary containing job requirements

    Returns:
        tuple: (is_valid: bool, error_message: Optional[str])
    """
    required_fields = ['role', 'skills']

    for field in required_fields:
        if field not in data or not data[field] or not data[field].strip():
            return False, f"'{field}' is required and cannot be empty"

    # Validate role length
    if len(data['role']) > 200:
        return False, "Role description is too long (max 200 characters)"

    # Validate skills
    if len(data['skills']) > 500:
        return False, "Skills list is too long (max 500 characters)"

    # Validate additional requirements
    if 'additional' in data and len(data.get('additional', '')) > 2000:
        return False, "Additional requirements too long (max 2000 characters)"

    return True, None


def validate_github_username(username: str) -> tuple[bool, Optional[str]]:
    """
    Validate GitHub username format

    Args:
        username: GitHub username to validate

    Returns:
        tuple: (is_valid: bool, error_message: Optional[str])
    """
    import re

    if not username or not username.strip():
        return False, "GitHub username cannot be empty"

    # GitHub username rules: 1-39 chars, alphanumeric and hyphens, cannot start/end with hyphen
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$'

    if not re.match(pattern, username):
        return False, "Invalid GitHub username format"

    if len(username) > 39:
        return False, "GitHub username too long (max 39 characters)"

    return True, None


def extract_candidate_name(text: str, filename: str) -> str:
    """Extract candidate name from resume text or filename"""
    import re

    # Try to find name in first few lines
    lines = [line.strip() for line in text.split('\n')[:10] if line.strip()]

    # Common patterns for names
    name_patterns = [
        r'^\s*(?:name|full name|candidate name|candidate|applicant)\s*[:\-]\s*(.+)$',
        r'^\s*(?:resume of|cv of|curriculum vitae of)\s*[:\-]?\s*(.+)$',
    ]

    for pattern in name_patterns:
        for line in lines:
            match = re.match(pattern, line, flags=re.I)
            if match:
                name = match.group(1).strip()
                if len(name.split()) <= 5 and '@' not in name:
                    return name

    # Fallback: use filename
    name = os.path.splitext(os.path.basename(filename))[0]
    name = name.replace('_', ' ').replace('-', ' ')
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def process_single_resume(resume_text: str, resume_filename: str, job_requirements: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Process a single resume and return candidate information

    Args:
        resume_text: Extracted text from resume
        resume_filename: Original filename
        job_requirements: Job requirements dict

    Returns:
        Dict with candidate info or None if processing failed
    """
    if not resume_text:
        return None

    candidate_name = extract_candidate_name(resume_text, resume_filename)
    score_result = score_candidate_resume(resume_text, job_requirements)

    # Extract skills from resume (simple keyword matching)
    skills_list = [s.strip() for s in job_requirements.get('skills', '').split(',') if s.strip()]
    found_skills = [skill for skill in skills_list
                   if skill.lower() in resume_text.lower()]

    return {
        'name': candidate_name,
        'score': score_result['score'],
        'matchScore': score_result['score'],
        'skills': found_skills,
        'note': f"Matched {len(found_skills)}/{len(skills_list)} required skills",
        'summary': f"Resume score: {score_result['score']}/100"
    }


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
@limiter.exempt  # Health check should not be rate limited
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'HireSight API',
        'api_keys_enabled': API_KEYS_ENABLED
    })


# ============================================================================
# FRONTEND ROUTES
# ============================================================================

@app.route('/')
@limiter.exempt
def home():
    """Serve the homepage"""
    return app.send_static_file('HIRESIGHT_HOME_PAGE/index.html')


@app.route('/company/register')
@limiter.exempt
def company_register():
    """Serve company registration page"""
    return app.send_static_file('COMPANY_REGISTRATION/index.html')


@app.route('/company/login')
@limiter.exempt
def company_login():
    """Serve company login page"""
    return app.send_static_file('COMPANY_LOGIN/index.html')


@app.route('/company/dashboard')
@limiter.exempt
def company_dashboard():
    """Serve company main page"""
    return app.send_static_file('COMPANY_MAIN_PAGE/index.html')


@app.route('/candidate/signup')
@limiter.exempt
def candidate_signup():
    """Serve candidate signup page"""
    return app.send_static_file('CANDIDATE_SIGNUP/index.html')


@app.route('/api/rank', methods=['POST'])
@require_api_key
@limiter.limit("10 per minute")  # Stricter limit for compute-intensive endpoint
def rank_candidates():
    """
    Rank candidates based on uploaded resumes and job requirements
    
    Expected form data:
    - role: Job title (string)
    - skills: Required skills (string, comma-separated)
    - experience: Required experience (string)
    - cgpa: Required CGPA (string)
    - additional: Additional requirements (string)
    - file: Resume file (zip, pdf, docx, doc)
    """
    try:
        # Extract job requirements
        role = request.form.get('role', '')
        skills = request.form.get('skills', '')
        experience = request.form.get('experience', '')
        cgpa = request.form.get('cgpa', '')
        additional = request.form.get('additional', '')

        job_requirements = {
            'role': role,
            'skills': skills,
            'experience': experience,
            'cgpa': cgpa,
            'additional': additional
        }

        # Validate job requirements
        is_valid, error_msg = validate_job_requirements(job_requirements)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Use .zip, .pdf, .docx, or .doc'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        candidates = []
        
        try:
            # Process based on file type
            if filename.endswith('.zip'):
                # Extract zip file securely
                extract_dir = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_extracted")
                os.makedirs(extract_dir, exist_ok=True)

                # Use secure extraction
                success, error_msg = safe_extract_zip(file_path, extract_dir)
                if not success:
                    # Cleanup and return error
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    if os.path.exists(extract_dir):
                        shutil.rmtree(extract_dir, ignore_errors=True)
                    return jsonify({'error': error_msg}), 400
                
                # Process each file in the zip
                for root, dirs, files in os.walk(extract_dir):
                    for resume_file in files:
                        if allowed_file(resume_file):
                            resume_path = os.path.join(root, resume_file)
                            resume_text = extract_text_from_file(resume_path)

                            candidate_data = process_single_resume(resume_text, resume_file, job_requirements)
                            if candidate_data:
                                candidates.append(candidate_data)
                
                # Cleanup extracted directory
                shutil.rmtree(extract_dir, ignore_errors=True)
                
            else:
                # Process single resume file
                resume_text = extract_text_from_file(file_path)

                candidate_data = process_single_resume(resume_text, filename, job_requirements)
                if candidate_data:
                    candidates.append(candidate_data)
            
            # Sort candidates by score (descending)
            candidates.sort(key=lambda x: x['score'], reverse=True)
            
            # Cleanup uploaded file
            os.remove(file_path)
            
            return jsonify({
                'success': True,
                'results': candidates,
                'count': len(candidates),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            # Cleanup on error
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/github/analyze', methods=['POST'])
@require_api_key
@limiter.limit("20 per minute")
def analyze_github():
    """
    Analyze a GitHub profile and return top 3 projects
    
    Expected JSON:
    {
        "username": "github_username",
        "job_requirements": {
            "role": "Backend Developer",
            "required_skills": ["Python", "Django", "PostgreSQL"],
            "preferred_skills": ["Docker", "AWS"]
        }
    }
    """
    try:
        data = request.get_json()

        if not data or 'username' not in data:
            return jsonify({'error': 'GitHub username is required'}), 400

        username = data['username']

        # Validate GitHub username
        is_valid, error_msg = validate_github_username(username)
        if not is_valid:
            return jsonify({'error': error_msg}), 400

        job_requirements = data.get('job_requirements', {})
        
        # Get GitHub token from environment
        github_token = os.environ.get('GITHUB_TOKEN')
        
        if not GitHubDataFetcher:
            return jsonify({'error': 'GitHub analysis module not available'}), 503
        
        # Fetch and analyze GitHub data
        fetcher = GitHubDataFetcher(access_token=github_token)
        analyzer = GitHubAnalyzer()
        
        # Fetch user data
        user_data = fetcher.fetch_user_profile(username)
        if not user_data:
            return jsonify({'error': 'Failed to fetch GitHub profile'}), 404
        
        # Fetch repositories (max 30 to find best ones)
        repos = fetcher.fetch_repositories(limit=30)
        
        # Get top 3 active repositories
        top_repos = fetcher.get_top_active_repos(repos, count=3)
        
        # Analyze
        analysis = analyzer.analyze_profile(user_data, repos)
        
        # Extract detailed project information for top 3
        top_projects = []
        for repo in top_repos:
            project_info = {
                'name': repo.get('name', ''),
                'description': repo.get('description', 'No description'),
                'url': repo.get('url', ''),
                'stars': repo.get('stargazers_count', 0),
                'forks': repo.get('forks_count', 0),
                'language': repo.get('language', 'Unknown'),
                'languages': repo.get('languages', {}),
                'topics': repo.get('topics', []),
                'created_at': repo.get('created_at', ''),
                'updated_at': repo.get('updated_at', ''),
                'open_issues': repo.get('open_issues_count', 0),
                'size_kb': repo.get('size', 0),
            }
            top_projects.append(project_info)
        
        # If job requirements provided, calculate match score
        match_score = None
        if job_requirements:
            matcher = CandidateMatcher(job_requirements)
            match_result = matcher.calculate_match_score(analysis)
            match_score = match_result.get('overall_score', 0)
        
        return jsonify({
            'success': True,
            'username': username,
            'analysis': analysis,
            'top_projects': top_projects,
            'match_score': match_score,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in GitHub analysis: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/interview/generate', methods=['POST'])
@require_api_key
@limiter.limit("5 per minute")  # Very strict - uses paid Gemini API
def generate_interview_questions():
    """
    Generate personalized interview questions
    
    Expected JSON:
    {
        "candidate_name": "John Doe",
        "candidate_profile": "Combined text from GitHub and LinkedIn",
        "api_key": "gemini_api_key" (optional, can be set in env)
    }
    """
    try:
        import requests as req
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        candidate_name = data.get('candidate_name', 'Candidate')
        candidate_profile = data.get('candidate_profile', '')
        
        if not candidate_profile:
            return jsonify({'error': 'Candidate profile text is required'}), 400
        
        # Get API key from request or environment
        api_key = data.get('api_key') or os.environ.get('GEMINI_API_KEY')

        if not api_key:
            return jsonify({
                'success': False,
                'error': 'Gemini API key is required. Set GEMINI_API_KEY environment variable.'
            }), 401

        model = "gemini-2.0-flash-exp"
        
        # Prepare prompt
        prompt = f"""
You are an expert technical interviewer and HR assistant.

You will receive a candidate profile containing combined text from their GitHub and LinkedIn profiles — including project details, skills, experiences, and technical achievements.

Generate a comprehensive interview guide with:
1. A 3-4 line thesis summary of the candidate's expertise
2. 8-10 technical questions based on their projects and skills
3. 3-5 behavioral/HR questions
4. 2-3 follow-up questions connecting their technical work to real-world use

Make questions personalized and specific to this candidate.

Candidate: {candidate_name}

Profile:
{candidate_profile[:5000]}
"""
        
        # Call Gemini API
        response = req.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )
        
        if response.status_code != 200:
            return jsonify({
                'error': f'Gemini API error: {response.status_code}',
                'details': response.text
            }), 500
        
        result = response.json()
        questions_text = result["candidates"][0]["content"]["parts"][0]["text"]
        
        return jsonify({
            'success': True,
            'candidate_name': candidate_name,
            'interview_questions': questions_text,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/leaderboard', methods=['POST'])
@require_api_key
def generate_leaderboard():
    """
    Generate leaderboard combining LinkedIn and GitHub scores
    
    Expected JSON:
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
    """
    try:
        data = request.get_json()
        
        if not data or 'candidates' not in data:
            return jsonify({'error': 'Candidates list is required'}), 400
        
        candidates = data['candidates']
        weights = data.get('weights', {'linkedin': 0.5, 'github': 0.5})
        
        # Calculate combined scores
        leaderboard = []
        for candidate in candidates:
            linkedin_score = candidate.get('linkedin_score', 0)
            github_score = candidate.get('github_score', 0)
            
            combined_score = (
                linkedin_score * weights.get('linkedin', 0.5) +
                github_score * weights.get('github', 0.5)
            )
            
            leaderboard.append({
                'name': candidate.get('name', 'Unknown'),
                'linkedin_score': linkedin_score,
                'github_score': github_score,
                'combined_score': round(combined_score, 2),
                'github_username': candidate.get('github_username', ''),
                'rank': 0  # Will be set after sorting
            })
        
        # Sort by combined score
        leaderboard.sort(key=lambda x: x['combined_score'], reverse=True)
        
        # Assign ranks
        for idx, candidate in enumerate(leaderboard, 1):
            candidate['rank'] = idx
        
        return jsonify({
            'success': True,
            'leaderboard': leaderboard,
            'count': len(leaderboard),
            'weights': weights,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/candidate/score-unified', methods=['POST'])
@require_api_key
@limiter.limit("10 per minute")
def score_candidate_unified():
    """
    Calculate unified candidate score integrating GitHub/LinkedIn and Resume data
    
    Expected form data or JSON:
    - candidate_name: Candidate's name (required)
    - job_description: JSON string with job requirements (required)
        {
            "role": "Backend Developer",
            "required_skills": ["Python", "Django", "PostgreSQL"],
            "preferred_skills": ["Docker", "AWS"],
            "description": "Full job description text",
            "experience": "3+ years"
        }
    - github_username: GitHub username (optional)
    - linkedin_data: JSON string with LinkedIn data (optional)
    - resume_file: Resume file (optional)
    - candidate_skills: JSON string with skills from GitHub/LinkedIn (optional)
        {
            "github": ["Python", "Django", "Docker"],
            "linkedin": ["Python", "PostgreSQL", "Leadership"]
        }
    - scoring_weights: JSON string with custom weights (optional)
        {
            "github_linkedin": 0.5,
            "resume": 0.5
        }
    - auto_extract_urls: Boolean to auto-extract GitHub/LinkedIn from resume (optional, default: true)
    """
    try:
        if not CandidateScorer:
            return jsonify({'error': 'Candidate scoring module not available'}), 503
        
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            candidate_name = data.get('candidate_name')
            job_description_str = data.get('job_description')
            github_username = data.get('github_username')
            linkedin_data_str = data.get('linkedin_data')
            candidate_skills_str = data.get('candidate_skills')
            scoring_weights_str = data.get('scoring_weights')
            resume_text = data.get('resume_text')
            auto_extract = data.get('auto_extract_urls', True)
        else:
            candidate_name = request.form.get('candidate_name')
            job_description_str = request.form.get('job_description')
            github_username = request.form.get('github_username')
            linkedin_data_str = request.form.get('linkedin_data')
            candidate_skills_str = request.form.get('candidate_skills')
            scoring_weights_str = request.form.get('scoring_weights')
            resume_text = None
            auto_extract = request.form.get('auto_extract_urls', 'true').lower() == 'true'
        
        # Validate required fields
        if not candidate_name:
            return jsonify({'error': 'candidate_name is required'}), 400
        
        if not job_description_str:
            return jsonify({'error': 'job_description is required'}), 400
        
        # Parse JSON strings
        try:
            job_description = json.loads(job_description_str) if isinstance(job_description_str, str) else job_description_str
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid job_description JSON'}), 400
        
        linkedin_data = None
        if linkedin_data_str:
            try:
                linkedin_data = json.loads(linkedin_data_str) if isinstance(linkedin_data_str, str) else linkedin_data_str
            except json.JSONDecodeError:
                logger.warning("Invalid LinkedIn data JSON, ignoring")
        
        candidate_skills = None
        if candidate_skills_str:
            try:
                candidate_skills = json.loads(candidate_skills_str) if isinstance(candidate_skills_str, str) else candidate_skills_str
            except json.JSONDecodeError:
                logger.warning("Invalid candidate_skills JSON, ignoring")
        
        scoring_weights = None
        if scoring_weights_str:
            try:
                scoring_weights = json.loads(scoring_weights_str) if isinstance(scoring_weights_str, str) else scoring_weights_str
            except json.JSONDecodeError:
                logger.warning("Invalid scoring_weights JSON, using defaults")
        
        # Handle resume file if uploaded
        extracted_contact_info = None
        if not request.is_json and 'resume_file' in request.files:
            file = request.files['resume_file']
            if file and file.filename and allowed_file(file.filename):
                # Save temporarily and extract text
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{filename}")
                file.save(file_path)
                
                try:
                    resume_text = extract_text_from_file(file_path)
                    
                    # Auto-extract URLs from resume if enabled
                    if auto_extract and ResumeURLExtractor and resume_text:
                        extractor = ResumeURLExtractor()
                        extracted_contact_info = extractor.extract_contact_info(resume_text)
                        
                        # Use extracted GitHub username if not provided
                        if not github_username and extracted_contact_info['github_username']:
                            github_username = extracted_contact_info['github_username']
                            logger.info(f"Auto-extracted GitHub username: {github_username}")
                        
                        # Use extracted LinkedIn if not provided
                        if not linkedin_data and extracted_contact_info['linkedin_url']:
                            logger.info(f"Auto-extracted LinkedIn URL: {extracted_contact_info['linkedin_url']}")
                finally:
                    # Cleanup
                    if os.path.exists(file_path):
                        os.remove(file_path)
        
        # Fetch GitHub analysis if username provided
        github_analysis = None
        if github_username and GitHubDataFetcher and GitHubAnalyzer:
            try:
                github_token = os.environ.get('GITHUB_TOKEN')
                fetcher = GitHubDataFetcher(token=github_token)
                analyzer = GitHubAnalyzer()
                
                user_data = fetcher.fetch_user_profile(github_username)
                if user_data:
                    repos = fetcher.fetch_user_repositories(github_username, max_repos=20)
                    github_analysis = analyzer.analyze_profile(user_data, repos)
                    logger.info(f"Fetched GitHub analysis for {github_username}")
            except Exception as e:
                logger.error(f"Error fetching GitHub data: {e}")
        
        # Initialize scorer and calculate scores
        scorer = CandidateScorer(job_description)
        
        result = scorer.score_candidate(
            candidate_name=candidate_name,
            resume_text=resume_text,
            github_analysis=github_analysis,
            linkedin_data=linkedin_data,
            candidate_skills=candidate_skills,
            weights=scoring_weights
        )
        
        # Add extracted contact info to response if available
        if extracted_contact_info:
            result['extracted_contact_info'] = {
                'email': extracted_contact_info['email'],
                'phone': extracted_contact_info['phone'],
                'github_url': extracted_contact_info['github_url'],
                'linkedin_url': extracted_contact_info['linkedin_url']
            }
        
        result['timestamp'] = datetime.now().isoformat()
        result['success'] = True
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in unified scoring: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/resume/extract-urls', methods=['POST'])
@require_api_key
@limiter.limit("20 per minute")
def extract_resume_urls():
    """
    Extract GitHub, LinkedIn, and other URLs from resume
    
    Expected form data:
    - resume_file: Resume file (pdf, docx, doc, txt)
    
    OR JSON:
    - resume_text: Resume text
    """
    try:
        if not ResumeURLExtractor:
            return jsonify({'error': 'Resume URL extractor not available'}), 503
        
        resume_text = None
        
        # Handle file upload
        if 'resume_file' in request.files:
            file = request.files['resume_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{filename}")
                file.save(file_path)
                
                try:
                    resume_text = extract_text_from_file(file_path)
                finally:
                    if os.path.exists(file_path):
                        os.remove(file_path)
        
        # Handle JSON with text
        elif request.is_json:
            data = request.get_json()
            resume_text = data.get('resume_text')
        
        if not resume_text:
            return jsonify({'error': 'No resume file or text provided'}), 400
        
        # Extract contact information
        extractor = ResumeURLExtractor()
        contact_info = extractor.extract_contact_info(resume_text)
        
        return jsonify({
            'success': True,
            'contact_info': contact_info,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error extracting URLs: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/candidates/score-batch', methods=['POST'])
@require_api_key
@limiter.limit("5 per minute")  # Stricter limit for batch processing
def score_candidates_batch():
    """
    Score multiple candidates and generate leaderboard with unified scoring
    
    Expected JSON:
    {
        "job_description": {
            "role": "Backend Developer",
            "required_skills": ["Python", "Django", "PostgreSQL"],
            "preferred_skills": ["Docker", "AWS"],
            "description": "Full job description",
            "experience": "3+ years"
        },
        "candidates": [
            {
                "name": "John Doe",
                "resume_text": "Resume content...",
                "github_username": "johndoe",
                "candidate_skills": {
                    "github": ["Python", "Django"],
                    "linkedin": ["PostgreSQL", "Leadership"]
                },
                "linkedin_data": {...}
            }
        ],
        "scoring_weights": {
            "github_linkedin": 0.5,
            "resume": 0.5
        }
    }
    """
    try:
        if not CandidateScorer:
            return jsonify({'error': 'Candidate scoring module not available'}), 503
        
        data = request.get_json()
        
        if not data or 'job_description' not in data:
            return jsonify({'error': 'job_description is required'}), 400
        
        if 'candidates' not in data or not data['candidates']:
            return jsonify({'error': 'candidates list is required and must not be empty'}), 400
        
        job_description = data['job_description']
        candidates = data['candidates']
        scoring_weights = data.get('scoring_weights')
        
        # Validate job description
        required_fields = ['role', 'required_skills']
        for field in required_fields:
            if field not in job_description:
                return jsonify({'error': f'job_description.{field} is required'}), 400
        
        # Initialize scorer
        scorer = CandidateScorer(job_description)
        
        # Fetch GitHub data for candidates if needed
        github_token = os.environ.get('GITHUB_TOKEN')
        if GitHubDataFetcher and GitHubAnalyzer:
            fetcher = GitHubDataFetcher(token=github_token)
            analyzer = GitHubAnalyzer()
            
            for candidate in candidates:
                github_username = candidate.get('github_username')
                if github_username and 'github_analysis' not in candidate:
                    try:
                        user_data = fetcher.fetch_user_profile(github_username)
                        if user_data:
                            repos = fetcher.fetch_user_repositories(github_username, max_repos=20)
                            candidate['github_analysis'] = analyzer.analyze_profile(user_data, repos)
                            logger.info(f"Fetched GitHub analysis for {github_username}")
                    except Exception as e:
                        logger.error(f"Error fetching GitHub data for {github_username}: {e}")
        
        # Score all candidates
        scored_candidates = scorer.score_multiple_candidates(candidates, weights=scoring_weights)
        
        return jsonify({
            'success': True,
            'leaderboard': scored_candidates,
            'count': len(scored_candidates),
            'job_description': job_description,
            'scoring_weights': scoring_weights or {'github_linkedin': 0.5, 'resume': 0.5},
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in batch scoring: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/analyze', methods=['POST'])
@require_api_key
@limiter.limit("15 per minute")
def analyze_resume():
    """
    Analyze a single resume and return detailed scores
    
    Expected form data:
    - resume: Resume file (pdf, docx, doc)
    """
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file uploaded'}), 400
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Save and process file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{filename}")
        file.save(file_path)
        
        try:
            # Extract text
            resume_text = extract_text_from_file(file_path)
            
            # Calculate various scores (simple heuristics)
            word_count = len(resume_text.split())
            
            # Keyword score: check for common resume keywords
            keywords = ['experience', 'skills', 'education', 'project', 'developed', 
                       'managed', 'led', 'achieved', 'implemented', 'designed']
            keyword_count = sum(1 for kw in keywords if kw.lower() in resume_text.lower())
            keyword_score = min(int((keyword_count / len(keywords)) * 100), 100)
            
            # Achievement score: look for numbers and action verbs
            import re
            numbers = len(re.findall(r'\b\d+%|\b\d+\+|\b\d+x\b', resume_text))
            action_verbs = ['increased', 'decreased', 'improved', 'reduced', 
                           'generated', 'achieved', 'exceeded']
            action_count = sum(1 for verb in action_verbs if verb.lower() in resume_text.lower())
            achievement_score = min(int(((numbers + action_count) / 15) * 100), 100)
            
            # Formatting score: check structure
            has_sections = sum(1 for section in ['experience', 'education', 'skills'] 
                              if section.lower() in resume_text.lower())
            formatting_score = min(int((has_sections / 3) * 100), 100)
            
            # Length score: optimal length
            if 300 <= word_count <= 800:
                length_score = 100
            elif word_count < 300:
                length_score = int((word_count / 300) * 100)
            else:
                length_score = max(int(100 - ((word_count - 800) / 20)), 50)
            
            # Main score: weighted average
            main_score = int((keyword_score * 0.3 + achievement_score * 0.3 + 
                            formatting_score * 0.2 + length_score * 0.2))
            
            # Cleanup
            os.remove(file_path)
            
            return jsonify({
                'success': True,
                'mainScore': main_score,
                'keywordScore': keyword_score,
                'achievementScore': achievement_score,
                'formattingScore': formatting_score,
                'lengthScore': length_score,
                'wordCount': word_count,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# EMAIL SENDING
# ============================================================================

@app.route('/api/email/send-interview-requests', methods=['POST'])
@limiter.limit("10 per minute")
def send_interview_requests():
    """
    Send interview requests to selected candidates

    Expected JSON:
    {
        "candidates": [
            {"name": "John Doe", "email": "john@example.com"},
            ...
        ],
        "questions": [
            "Question 1",
            "Question 2",
            ...
        ] (optional)
    }
    """
    try:
        data = request.get_json()

        if not data or 'candidates' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing candidates data'
            }), 400

        candidates = data['candidates']
        questions = data.get('questions', [])

        if not isinstance(candidates, list) or len(candidates) == 0:
            return jsonify({
                'success': False,
                'error': 'Candidates must be a non-empty list'
            }), 400

        # Log the email requests
        logger.info(f"📧 Email interview requests to {len(candidates)} candidates")
        for candidate in candidates:
            logger.info(f"  → {candidate.get('name')} ({candidate.get('email')})")

        # TODO: Integrate with actual email service (SendGrid, AWS SES, SMTP, etc.)
        # For now, we'll just log the requests and return success
        # You can integrate your preferred email service here

        # Example integration points:
        # 1. SMTP: Use smtplib to send emails via SMTP
        # 2. SendGrid: Use sendgrid Python library
        # 3. AWS SES: Use boto3 to send via Amazon SES
        # 4. Mailgun: Use requests to call Mailgun API

        # For demonstration, we're returning success
        # In production, you would actually send emails here

        return jsonify({
            'success': True,
            'message': f'Interview requests sent to {len(candidates)} candidates',
            'recipients': [c.get('email') for c in candidates],
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error sending interview requests: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# COMPREHENSIVE RESUME PARSING ENDPOINT
# ============================================================================

@app.route('/api/resume/parse-comprehensive', methods=['POST'])
@require_api_key
@limiter.limit("20 per minute")
def parse_comprehensive_resumes():
    """
    Parse resumes comprehensively and extract ALL candidate information:
    - Name, Email, Phone, Location
    - Education, University, CGPA
    - Experience (years), Projects count
    - Technical Skills
    - GitHub, LinkedIn
    - Professional Summary

    Accepts ZIP file with multiple resumes or single resume file (PDF, DOCX, TXT)

    Returns detailed candidate profiles with all fields populated
    """
    try:
        # Import comprehensive parser
        import sys
        utils_path = os.path.join(os.path.dirname(__file__), 'utils')
        if utils_path not in sys.path:
            sys.path.insert(0, utils_path)

        from comprehensive_resume_parser import parse_comprehensive_resume

        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file type. Use .zip, .pdf, .docx, .doc, or .txt'
            }), 400

        # Get optional parameters
        use_ai = request.form.get('use_ai', 'true').lower() == 'true'
        calculate_score = request.form.get('calculate_score', 'false').lower() == 'true'

        # Job requirements for scoring (optional)
        job_requirements = None
        if calculate_score:
            job_requirements = {
                'role': request.form.get('role', ''),
                'skills': request.form.get('skills', ''),
                'experience': request.form.get('experience', ''),
                'cgpa': request.form.get('cgpa', ''),
                'additional': request.form.get('additional', '')
            }

        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)

        candidates = []

        try:
            # Process based on file type
            if filename.endswith('.zip'):
                # Extract zip file securely
                extract_dir = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_extracted")
                os.makedirs(extract_dir, exist_ok=True)

                # Use secure extraction
                success, error_msg = safe_extract_zip(file_path, extract_dir)
                if not success:
                    # Cleanup and return error
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    if os.path.exists(extract_dir):
                        shutil.rmtree(extract_dir, ignore_errors=True)
                    return jsonify({'error': error_msg}), 400

                # Process each file in the zip
                for root, dirs, files in os.walk(extract_dir):
                    for resume_file in files:
                        if allowed_file(resume_file):
                            resume_path = os.path.join(root, resume_file)
                            resume_text = extract_text_from_file(resume_path)

                            if resume_text:
                                # Parse comprehensively
                                candidate_data = parse_comprehensive_resume(resume_text, use_ai=use_ai)

                                # Add filename for reference
                                candidate_data['filename'] = resume_file

                                # Calculate match score if requested
                                if calculate_score and job_requirements:
                                    score_result = score_candidate_resume(resume_text, job_requirements)
                                    candidate_data['score'] = score_result['score']
                                    candidate_data['matchScore'] = score_result['score']
                                else:
                                    # Default score based on data completeness
                                    completeness = sum([
                                        bool(candidate_data.get('email')),
                                        bool(candidate_data.get('phone')),
                                        bool(candidate_data.get('education')),
                                        bool(candidate_data.get('skills')),
                                        bool(candidate_data.get('github')) or bool(candidate_data.get('linkedin')),
                                        candidate_data.get('experience_years', 0) > 0,
                                        candidate_data.get('cgpa', 0) > 0
                                    ])
                                    candidate_data['score'] = int((completeness / 7) * 100)
                                    candidate_data['matchScore'] = candidate_data['score']

                                # Format experience and projects for display
                                candidate_data['exp'] = f"{candidate_data.get('experience_years', 0)} yrs"
                                candidate_data['projects'] = candidate_data.get('projects_count', 0)

                                # Format note
                                skills_count = len(candidate_data.get('skills', []))
                                candidate_data['note'] = candidate_data.get('summary', '') or \
                                                        f"Proficient in {skills_count}+ technologies"

                                candidates.append(candidate_data)

                # Cleanup extracted directory
                shutil.rmtree(extract_dir, ignore_errors=True)

            else:
                # Process single resume file
                resume_text = extract_text_from_file(file_path)

                if resume_text:
                    # Parse comprehensively
                    candidate_data = parse_comprehensive_resume(resume_text, use_ai=use_ai)

                    # Add filename for reference
                    candidate_data['filename'] = filename

                    # Calculate match score if requested
                    if calculate_score and job_requirements:
                        score_result = score_candidate_resume(resume_text, job_requirements)
                        candidate_data['score'] = score_result['score']
                        candidate_data['matchScore'] = score_result['score']
                    else:
                        # Default score based on data completeness
                        completeness = sum([
                            bool(candidate_data.get('email')),
                            bool(candidate_data.get('phone')),
                            bool(candidate_data.get('education')),
                            bool(candidate_data.get('skills')),
                            bool(candidate_data.get('github')) or bool(candidate_data.get('linkedin')),
                            candidate_data.get('experience_years', 0) > 0,
                            candidate_data.get('cgpa', 0) > 0
                        ])
                        candidate_data['score'] = int((completeness / 7) * 100)
                        candidate_data['matchScore'] = candidate_data['score']

                    # Format experience and projects for display
                    candidate_data['exp'] = f"{candidate_data.get('experience_years', 0)} yrs"
                    candidate_data['projects'] = candidate_data.get('projects_count', 0)

                    # Format note
                    skills_count = len(candidate_data.get('skills', []))
                    candidate_data['note'] = candidate_data.get('summary', '') or \
                                            f"Proficient in {skills_count}+ technologies"

                    candidates.append(candidate_data)

            # Sort candidates by score (descending)
            candidates.sort(key=lambda x: x.get('score', 0), reverse=True)

            # Cleanup uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)

            logger.info(f"Successfully parsed {len(candidates)} resumes comprehensively")

            return jsonify({
                'success': True,
                'results': candidates,
                'count': len(candidates),
                'timestamp': datetime.now().isoformat(),
                'parsing_method': 'AI-powered' if use_ai else 'Regex-based'
            })

        except Exception as e:
            # Cleanup on error
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e

    except Exception as e:
        logger.error(f"Error in comprehensive resume parsing: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# CATCH-ALL ROUTE FOR STATIC FILES
# ============================================================================

@app.route('/<path:path>')
@limiter.exempt
def serve_static(path):
    """Serve static files (CSS, JS, images) - Must be last route"""
    try:
        return app.send_static_file(path)
    except Exception as e:
        # If file not found, return 404
        logger.debug(f"Static file not found: {path}")
        return jsonify({'error': 'File not found'}), 404


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🚀 HireSight Unified API Server")
    logger.info("=" * 60)
    logger.info(f"📁 Upload folder: {UPLOAD_FOLDER}")
    logger.info(f"📊 Max file size: {MAX_FILE_SIZE / (1024*1024):.1f} MB")
    logger.info(f"✅ Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}")
    logger.info(f"🌐 Serving frontend from: {FRONTEND_DIR}")
    logger.info("=" * 60)
    logger.info("\nFrontend routes:")
    logger.info("  GET  / - Homepage")
    logger.info("  GET  /company/register - Company registration")
    logger.info("  GET  /company/login - Company login")
    logger.info("  GET  /company/dashboard - Company dashboard")
    logger.info("  GET  /candidate/signup - Candidate signup")
    logger.info("\nAPI endpoints:")
    logger.info("  GET  /api/health - Health check")
    logger.info("  POST /api/rank - Rank candidates from resumes")
    logger.info("  POST /api/analyze - Analyze single resume")
    logger.info("  POST /api/github/analyze - Analyze GitHub profile")
    logger.info("  POST /api/interview/generate - Generate interview questions")
    logger.info("  POST /api/leaderboard - Generate combined leaderboard")
    logger.info("  POST /api/candidate/score-unified - Score single candidate (unified)")
    logger.info("  POST /api/candidates/score-batch - Score multiple candidates (unified)")
    logger.info("  POST /api/resume/extract-urls - Extract URLs from resume")
    logger.info("=" * 60)

    # Run server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'

    app.run(host='0.0.0.0', port=port, debug=debug)
