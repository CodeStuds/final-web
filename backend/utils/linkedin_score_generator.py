#!/usr/bin/env python3
"""
LinkedIn Score Generator
Calculates resume-job description similarity scores and generates results.csv
Compatible with the leaderboard system's expected format
"""

import os
import csv
import logging
from typing import Dict, List, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)


class LinkedInScoreGenerator:
    """
    Generates LinkedIn-style similarity scores between resumes and job descriptions
    Outputs results.csv compatible with leaderboard system
    """
    
    def __init__(self):
        """Initialize the score generator"""
        self.vectorizer = None
    
    def calculate_similarity_score(
        self,
        resume_text: str,
        job_description: str
    ) -> float:
        """
        Calculate cosine similarity between resume and job description
        
        Args:
            resume_text: Full text content of the resume
            job_description: Job description text
            
        Returns:
            float: Similarity score between 0 and 1
        """
        try:
            # Handle empty inputs
            if not resume_text or not resume_text.strip():
                logger.warning("Empty resume text provided")
                return 0.0
            
            if not job_description or not job_description.strip():
                logger.warning("Empty job description provided")
                return 0.0
            
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=500,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1
            )
            
            # Vectorize texts
            try:
                tfidf_matrix = vectorizer.fit_transform([job_description, resume_text])
            except ValueError as e:
                logger.warning(f"Vectorization failed: {e}")
                return 0.0
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Ensure score is between 0 and 1
            score = max(0.0, min(1.0, float(similarity)))
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating similarity score: {e}")
            return 0.0
    
    def generate_scores_for_candidates(
        self,
        candidates: List[Dict[str, Any]],
        job_description: str,
        session_dir: str
    ) -> str:
        """
        Generate similarity scores for all candidates and save to results.csv
        
        Args:
            candidates: List of candidate dictionaries with 'name' and 'text' fields
            job_description: Job description text to compare against
            session_dir: Session directory to save results.csv
            
        Returns:
            str: Path to generated results.csv file
            
        Raises:
            ValueError: If candidates list is empty or invalid
        """
        if not candidates:
            raise ValueError("Candidates list cannot be empty")
        
        if not job_description or not job_description.strip():
            raise ValueError("Job description cannot be empty")
        
        logger.info(f"Generating scores for {len(candidates)} candidates")
        
        # Calculate scores for each candidate
        results = []
        for candidate in candidates:
            name = candidate.get('name', 'Unknown')
            resume_text = candidate.get('text', '')
            
            # Calculate similarity score
            score = self.calculate_similarity_score(resume_text, job_description)
            
            results.append({
                'Candidate': name,
                'Score': round(score, 4)  # Round to 4 decimal places
            })
            
            logger.debug(f"Candidate: {name}, Score: {score:.4f}")
        
        # Sort by score (descending)
        results.sort(key=lambda x: x['Score'], reverse=True)
        
        # Save to CSV in leaderboard format
        csv_path = os.path.join(session_dir, 'results.csv')
        
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['Candidate', 'Score'])
                writer.writeheader()
                writer.writerows(results)
            
            logger.info(f"✅ Saved LinkedIn scores to: {csv_path}")
            
            # Log statistics
            scores = [r['Score'] for r in results]
            if scores:
                logger.info(f"Score statistics - Min: {min(scores):.4f}, "
                          f"Max: {max(scores):.4f}, "
                          f"Mean: {np.mean(scores):.4f}")
            
            return csv_path
            
        except Exception as e:
            logger.error(f"Failed to save results.csv: {e}")
            raise
    
    def build_job_description_from_requirements(
        self,
        requirements: Dict[str, Any]
    ) -> str:
        """
        Build a comprehensive job description text from structured requirements
        
        Args:
            requirements: Dictionary with job requirements fields
                - role: Job title
                - skills: Required skills
                - experience: Experience requirements
                - cgpa: CGPA requirements
                - additional: Additional requirements
                - description: Full job description (optional)
                
        Returns:
            str: Formatted job description text
        """
        parts = []
        
        # Job title/role
        if requirements.get('role'):
            parts.append(f"Job Role: {requirements['role']}")
        
        # Skills
        if requirements.get('skills'):
            skills = requirements['skills']
            if isinstance(skills, list):
                skills = ', '.join(skills)
            parts.append(f"Required Skills: {skills}")
        
        # Experience
        if requirements.get('experience'):
            parts.append(f"Experience Required: {requirements['experience']}")
        
        # CGPA
        if requirements.get('cgpa'):
            parts.append(f"CGPA Requirement: {requirements['cgpa']}")
        
        # Additional requirements
        if requirements.get('additional'):
            parts.append(f"Additional Requirements: {requirements['additional']}")
        
        # Full description if provided
        if requirements.get('description'):
            parts.append(f"Job Description: {requirements['description']}")
        
        # Combine all parts
        job_description = '\n\n'.join(parts)
        
        if not job_description.strip():
            logger.warning("Empty job description generated from requirements")
            return "General software development position"
        
        return job_description
    
    def update_scores_in_session(
        self,
        session_dir: str,
        candidates: List[Dict[str, Any]],
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Complete workflow: build job description and generate scores
        
        Args:
            session_dir: Session directory to save results
            candidates: List of candidates with resume text
            job_requirements: Job requirements dictionary
            
        Returns:
            dict: Summary of generated scores
        """
        # Build job description
        job_description = self.build_job_description_from_requirements(job_requirements)
        
        logger.info(f"Job description length: {len(job_description)} characters")
        
        # Generate scores
        csv_path = self.generate_scores_for_candidates(
            candidates,
            job_description,
            session_dir
        )
        
        # Calculate statistics
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            scores = [float(row['Score']) for row in reader]
        
        return {
            'success': True,
            'csv_path': csv_path,
            'total_candidates': len(scores),
            'average_score': round(np.mean(scores), 4) if scores else 0,
            'max_score': round(max(scores), 4) if scores else 0,
            'min_score': round(min(scores), 4) if scores else 0
        }


# Convenience function
def create_linkedin_score_generator() -> LinkedInScoreGenerator:
    """
    Create a LinkedInScoreGenerator instance
    
    Returns:
        LinkedInScoreGenerator: Configured generator
    """
    return LinkedInScoreGenerator()


def generate_linkedin_scores(
    candidates: List[Dict[str, Any]],
    job_requirements: Dict[str, Any],
    session_dir: str
) -> Dict[str, Any]:
    """
    Convenience function to generate LinkedIn scores
    
    Args:
        candidates: List of candidates with name and text
        job_requirements: Job requirements dictionary
        session_dir: Session directory for output
        
    Returns:
        dict: Summary of generated scores
    """
    generator = create_linkedin_score_generator()
    return generator.update_scores_in_session(session_dir, candidates, job_requirements)
