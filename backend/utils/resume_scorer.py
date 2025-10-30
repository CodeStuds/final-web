#!/usr/bin/env python3
"""
Resume Scoring and Matching Utility
Matches resumes against job descriptions using TF-IDF and cosine similarity
Converted from Colab script to standalone utility
"""

import os
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. Resume scoring disabled.")


class ResumeScorer:
    """Score and rank resumes against job description"""
    
    def __init__(self):
        """Initialize the scorer"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required for resume scoring")
        
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1
        )
    
    def clean_name_from_filename(self, filename: str) -> str:
        """Extract and clean candidate name from filename"""
        name = os.path.splitext(os.path.basename(filename))[0]
        # Remove common extraction headers
        name = re.sub(r'={2,}.*EXTRACTED\s+FROM[:\s\-]*', '', name, flags=re.I)
        # Replace delimiters
        name = name.replace('_', ' ').replace('-', ' ').strip(' =._-')
        # Collapse spaces
        name = re.sub(r'\s+', ' ', name).strip()
        return name or filename
    
    def extract_name_from_text(self, text: str, fallback: str = "") -> str:
        """
        Attempt to extract candidate name from resume text
        Uses simple heuristics - first few non-empty lines
        """
        if not text:
            return fallback
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if not lines:
            return fallback
        
        # Usually the name is in the first 3 lines
        for line in lines[:3]:
            # Skip lines that look like headers or sections
            if len(line) > 50 or any(keyword in line.lower() for keyword in [
                'resume', 'curriculum', 'cv', 'contact', 'email', 'phone', 'address'
            ]):
                continue
            
            # Check if line looks like a name (2-4 words, reasonable length)
            words = line.split()
            if 2 <= len(words) <= 4 and 5 <= len(line) <= 50:
                return line
        
        return fallback
    
    def score_resumes(
        self,
        job_description: str,
        resumes: List[Dict[str, str]],
        top_n: Optional[int] = None
    ) -> List[Dict[str, any]]:
        """
        Score and rank resumes against job description
        
        Args:
            job_description: Job description text
            resumes: List of dicts with 'text' and 'filename' or 'name'
            top_n: Return only top N results (None = all)
            
        Returns:
            List of scored resumes sorted by score descending
        """
        if not SKLEARN_AVAILABLE:
            raise RuntimeError("scikit-learn not available")
        
        if not resumes:
            return []
        
        # Prepare documents
        all_texts = [job_description] + [r['text'] for r in resumes]
        
        try:
            # Compute TF-IDF vectors
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Compute cosine similarity between job description and each resume
            job_vector = tfidf_matrix[0:1]
            resume_vectors = tfidf_matrix[1:]
            
            similarities = cosine_similarity(job_vector, resume_vectors)[0]
            
            # Build results
            results = []
            for i, resume in enumerate(resumes):
                score = float(similarities[i]) * 100  # Convert to percentage
                
                # Try to get candidate name
                name = resume.get('name')
                if not name:
                    filename = resume.get('filename', f'resume_{i}')
                    name = self.extract_name_from_text(
                        resume['text'],
                        fallback=self.clean_name_from_filename(filename)
                    )
                
                results.append({
                    'name': name,
                    'score': round(score, 2),
                    'filename': resume.get('filename', f'resume_{i}'),
                    'text_length': len(resume['text'])
                })
            
            # Sort by score descending
            results.sort(key=lambda x: x['score'], reverse=True)
            
            # Return top N if specified
            if top_n:
                results = results[:top_n]
            
            return results
        
        except Exception as e:
            logger.error(f"Error scoring resumes: {e}")
            raise


def score_resumes_simple(
    job_description: str,
    resume_texts: List[str],
    resume_names: Optional[List[str]] = None
) -> List[Dict[str, any]]:
    """
    Convenience function to score resumes
    
    Args:
        job_description: Job description text
        resume_texts: List of resume text content
        resume_names: Optional list of candidate names
        
    Returns:
        List of scored results
    """
    if not SKLEARN_AVAILABLE:
        raise ImportError("scikit-learn is required")
    
    # Prepare resume data
    resumes = []
    for i, text in enumerate(resume_texts):
        resume = {
            'text': text,
            'filename': f'resume_{i}.txt'
        }
        if resume_names and i < len(resume_names):
            resume['name'] = resume_names[i]
        resumes.append(resume)
    
    scorer = ResumeScorer()
    return scorer.score_resumes(job_description, resumes)


if __name__ == '__main__':
    # Example usage
    job_desc = """
    Looking for a Python developer with experience in:
    - Django/Flask frameworks
    - REST API development
    - PostgreSQL database
    - Docker and Kubernetes
    - Agile methodologies
    """
    
    resumes = [
        {
            'text': 'Python developer with 5 years Django experience. Built REST APIs. PostgreSQL expert.',
            'filename': 'john_doe.txt'
        },
        {
            'text': 'Frontend developer with React and JavaScript. Some Python experience.',
            'filename': 'jane_smith.txt'
        },
        {
            'text': 'Full-stack engineer. Python, Django, Flask, Docker, Kubernetes. PostgreSQL and MySQL.',
            'filename': 'bob_jones.txt'
        }
    ]
    
    scorer = ResumeScorer()
    results = scorer.score_resumes(job_desc, resumes)
    
    print("\nCandidate Ranking:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['name']} - Score: {result['score']:.2f}")
