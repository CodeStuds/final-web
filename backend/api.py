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
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Add backend subdirectories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'github-data-fetch'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ibhanwork'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'leaderboard'))

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
        print("Warning: GitHub modules not available")
        GitHubDataFetcher = None
        GitHubAnalyzer = None
        CandidateMatcher = None


# Configuration
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# File upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'zip', 'pdf', 'docx', 'doc', 'txt'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
            print(f"Error extracting PDF: {e}")
            return ""


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX files"""
    try:
        from docx import Document
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f"Error extracting DOCX: {e}")
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
        print(f"Error calculating score: {e}")
        score = 50.0  # Default score
    
    return {
        'score': score,
        'similarity': similarity if 'similarity' in locals() else 0.5
    }


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


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'HireSight API'
    })


@app.route('/api/rank', methods=['POST'])
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
                # Extract zip file
                extract_dir = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_extracted")
                os.makedirs(extract_dir, exist_ok=True)
                
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                # Process each file in the zip
                for root, dirs, files in os.walk(extract_dir):
                    for resume_file in files:
                        if allowed_file(resume_file):
                            resume_path = os.path.join(root, resume_file)
                            resume_text = extract_text_from_file(resume_path)
                            
                            if resume_text:
                                candidate_name = extract_candidate_name(resume_text, resume_file)
                                score_result = score_candidate_resume(resume_text, job_requirements)
                                
                                # Extract skills from resume (simple keyword matching)
                                skills_list = [s.strip() for s in skills.split(',') if s.strip()]
                                found_skills = [skill for skill in skills_list 
                                               if skill.lower() in resume_text.lower()]
                                
                                candidates.append({
                                    'name': candidate_name,
                                    'score': score_result['score'],
                                    'matchScore': score_result['score'],
                                    'skills': found_skills,
                                    'note': f"Matched {len(found_skills)}/{len(skills_list)} required skills",
                                    'summary': f"Resume score: {score_result['score']}/100"
                                })
                
                # Cleanup extracted directory
                shutil.rmtree(extract_dir, ignore_errors=True)
                
            else:
                # Process single resume file
                resume_text = extract_text_from_file(file_path)
                
                if resume_text:
                    candidate_name = extract_candidate_name(resume_text, filename)
                    score_result = score_candidate_resume(resume_text, job_requirements)
                    
                    skills_list = [s.strip() for s in skills.split(',') if s.strip()]
                    found_skills = [skill for skill in skills_list 
                                   if skill.lower() in resume_text.lower()]
                    
                    candidates.append({
                        'name': candidate_name,
                        'score': score_result['score'],
                        'matchScore': score_result['score'],
                        'skills': found_skills,
                        'note': f"Matched {len(found_skills)}/{len(skills_list)} required skills",
                        'summary': f"Resume score: {score_result['score']}/100"
                    })
            
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
def analyze_github():
    """
    Analyze a GitHub profile
    
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
        job_requirements = data.get('job_requirements', {})
        
        # Get GitHub token from environment
        github_token = os.environ.get('GITHUB_TOKEN')
        
        if not GitHubDataFetcher:
            return jsonify({'error': 'GitHub analysis module not available'}), 503
        
        # Fetch and analyze GitHub data
        fetcher = GitHubDataFetcher(token=github_token)
        analyzer = GitHubAnalyzer()
        
        # Fetch user data
        user_data = fetcher.fetch_user_profile(username)
        if not user_data:
            return jsonify({'error': 'Failed to fetch GitHub profile'}), 404
        
        repos = fetcher.fetch_user_repositories(username, max_repos=20)
        
        # Analyze
        analysis = analyzer.analyze_profile(user_data, repos)
        
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
            'match_score': match_score,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/interview/generate', methods=['POST'])
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
        api_key = data.get('api_key') or os.environ.get('GEMINI_API_KEY', 'AIzaSyDg73KGgHkLntpyI_S9Dbho93zfu4EJOxg')
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


@app.route('/api/analyze', methods=['POST'])
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
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 HireSight Unified API Server")
    print("=" * 60)
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"📊 Max file size: {MAX_FILE_SIZE / (1024*1024):.1f} MB")
    print(f"✅ Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}")
    print("=" * 60)
    print("\nAvailable endpoints:")
    print("  GET  /api/health - Health check")
    print("  POST /api/rank - Rank candidates from resumes")
    print("  POST /api/analyze - Analyze single resume")
    print("  POST /api/github/analyze - Analyze GitHub profile")
    print("  POST /api/interview/generate - Generate interview questions")
    print("  POST /api/leaderboard - Generate combined leaderboard")
    print("=" * 60)
    
    # Run server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
