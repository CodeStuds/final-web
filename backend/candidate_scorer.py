#!/usr/bin/env python3
"""
Unified Candidate Scoring Module
Integrates GitHub/LinkedIn skills matching with resume-based scoring
to generate final averaged leaderboard scores
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logger = logging.getLogger(__name__)


class CompatibilityScorer:
    """
    Calculates compatibility scores between candidate skills and job requirements
    Integrates GitHub/LinkedIn data with resume-based scoring
    """
    
    def __init__(self, job_description: Dict[str, Any]):
        """
        Initialize the scorer with job description
        
        Args:
            job_description: Dictionary containing:
                - role: Job title (str)
                - required_skills: List of required skills (list)
                - preferred_skills: List of preferred skills (list)
                - description: Full job description text (str)
                - experience: Required experience (str, optional)
        """
        self.job_description = job_description
        self.required_skills = [s.strip().lower() for s in job_description.get('required_skills', [])]
        self.preferred_skills = [s.strip().lower() for s in job_description.get('preferred_skills', [])]
        self.job_text = self._build_job_text()
        
        logger.info(f"Initialized CompatibilityScorer with {len(self.required_skills)} required skills")
    
    def _build_job_text(self) -> str:
        """Build comprehensive job description text for similarity matching"""
        parts = []
        
        if 'role' in self.job_description:
            parts.append(f"Role: {self.job_description['role']}")
        
        if self.required_skills:
            parts.append(f"Required Skills: {', '.join(self.required_skills)}")
        
        if self.preferred_skills:
            parts.append(f"Preferred Skills: {', '.join(self.preferred_skills)}")
        
        if 'description' in self.job_description:
            parts.append(self.job_description['description'])
        
        if 'experience' in self.job_description:
            parts.append(f"Experience: {self.job_description['experience']}")
        
        return '\n'.join(parts)
    
    def calculate_github_linkedin_compatibility(
        self,
        candidate_skills: Dict[str, Any],
        github_analysis: Optional[Dict[str, Any]] = None,
        linkedin_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate compatibility score from GitHub and LinkedIn data
        
        Args:
            candidate_skills: Dictionary with 'github' and 'linkedin' skills
            github_analysis: Full GitHub analysis data (optional)
            linkedin_data: LinkedIn profile data (optional)
        
        Returns:
            Dictionary containing:
                - compatibility_score: Score between 0 and 1
                - skill_match_score: Skill overlap score (0-1)
                - required_skills_matched: List of matched required skills
                - preferred_skills_matched: List of matched preferred skills
                - missing_skills: List of missing required skills
                - additional_skills: Skills candidate has beyond requirements
                - confidence: Confidence level of the scoring
        """
        # Collect all candidate skills from various sources
        all_candidate_skills = set()
        skill_confidence = {}
        
        # Extract GitHub skills
        if github_analysis:
            github_skills = github_analysis.get('skills_analysis', {}).get('skills', {})
            for skill_name, skill_data in github_skills.items():
                skill_lower = skill_name.lower()
                all_candidate_skills.add(skill_lower)
                skill_confidence[skill_lower] = skill_data.get('confidence', 50) / 100
        
        # Extract LinkedIn skills
        if linkedin_data and 'skills' in linkedin_data:
            for skill in linkedin_data['skills']:
                skill_lower = skill.lower()
                all_candidate_skills.add(skill_lower)
                # LinkedIn skills get default confidence of 0.7
                if skill_lower not in skill_confidence:
                    skill_confidence[skill_lower] = 0.7
        
        # Extract from simplified candidate_skills dict
        if 'github' in candidate_skills:
            for skill in candidate_skills['github']:
                skill_lower = skill.lower()
                all_candidate_skills.add(skill_lower)
                if skill_lower not in skill_confidence:
                    skill_confidence[skill_lower] = 0.6
        
        if 'linkedin' in candidate_skills:
            for skill in candidate_skills['linkedin']:
                skill_lower = skill.lower()
                all_candidate_skills.add(skill_lower)
                if skill_lower not in skill_confidence:
                    skill_confidence[skill_lower] = 0.7
        
        logger.info(f"Candidate has {len(all_candidate_skills)} total skills")
        
        # Match required skills
        required_matched = []
        for req_skill in self.required_skills:
            if self._skill_matches(req_skill, all_candidate_skills):
                required_matched.append(req_skill)
        
        # Match preferred skills
        preferred_matched = []
        for pref_skill in self.preferred_skills:
            if self._skill_matches(pref_skill, all_candidate_skills):
                preferred_matched.append(pref_skill)
        
        # Calculate skill match score
        # Required skills: 70% weight, Preferred skills: 30% weight
        required_score = (len(required_matched) / len(self.required_skills)) if self.required_skills else 1.0
        preferred_score = (len(preferred_matched) / len(self.preferred_skills)) if self.preferred_skills else 0.0
        
        skill_match_score = (required_score * 0.7) + (preferred_score * 0.3)
        
        # Calculate weighted skill quality (using confidence scores)
        matched_skill_quality = 0.0
        if required_matched or preferred_matched:
            all_matched = required_matched + preferred_matched
            quality_sum = sum(skill_confidence.get(skill, 0.5) for skill in all_matched)
            matched_skill_quality = quality_sum / len(all_matched)
        
        # Final compatibility score combines match rate with quality
        compatibility_score = (skill_match_score * 0.8) + (matched_skill_quality * 0.2)
        
        # Identify missing and additional skills
        missing_skills = [s for s in self.required_skills if not self._skill_matches(s, all_candidate_skills)]
        additional_skills = list(all_candidate_skills - set(self.required_skills) - set(self.preferred_skills))
        
        # Calculate confidence based on data sources
        confidence = 0.5
        if github_analysis:
            confidence += 0.3
        if linkedin_data:
            confidence += 0.2
        confidence = min(confidence, 1.0)
        
        return {
            'compatibility_score': round(compatibility_score, 4),
            'skill_match_score': round(skill_match_score, 4),
            'required_skills_matched': required_matched,
            'required_skills_missing': missing_skills,
            'preferred_skills_matched': preferred_matched,
            'additional_skills': additional_skills[:10],  # Limit to top 10
            'match_percentage': round(required_score * 100, 2),
            'confidence': round(confidence, 2),
            'skill_quality': round(matched_skill_quality, 4)
        }
    
    def _skill_matches(self, target_skill: str, candidate_skills: set) -> bool:
        """
        Check if a target skill matches any candidate skill
        Handles partial matches and common variations
        """
        target_lower = target_skill.lower()
        
        # Direct match
        if target_lower in candidate_skills:
            return True
        
        # Partial match (e.g., "javascript" matches "node.js", "react.js")
        for candidate_skill in candidate_skills:
            if target_lower in candidate_skill or candidate_skill in target_lower:
                return True
        
        # Common variations
        skill_variations = {
            'javascript': ['js', 'node', 'nodejs', 'react', 'vue', 'angular'],
            'python': ['py', 'django', 'flask', 'fastapi'],
            'docker': ['containers', 'containerization'],
            'kubernetes': ['k8s'],
            'postgresql': ['postgres', 'psql'],
            'mysql': ['sql'],
            'mongodb': ['mongo', 'nosql'],
        }
        
        if target_lower in skill_variations:
            for variation in skill_variations[target_lower]:
                if variation in candidate_skills:
                    return True
        
        return False
    
    def calculate_resume_compatibility(self, resume_text: str) -> Dict[str, Any]:
        """
        Calculate compatibility score from resume text using TF-IDF similarity
        
        Args:
            resume_text: Extracted text from resume
        
        Returns:
            Dictionary containing:
                - compatibility_score: Score between 0 and 1
                - similarity_score: Raw cosine similarity
                - matched_keywords: Keywords found in resume
        """
        if not resume_text or not resume_text.strip():
            return {
                'compatibility_score': 0.0,
                'similarity_score': 0.0,
                'matched_keywords': [],
                'error': 'Empty resume text'
            }
        
        try:
            # Use TF-IDF vectorization
            vectorizer = TfidfVectorizer(
                stop_words='english',
                lowercase=True,
                ngram_range=(1, 2),
                min_df=1,
                max_features=5000
            )
            
            # Create corpus
            corpus = [self.job_text, resume_text]
            tfidf_matrix = vectorizer.fit_transform(corpus)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Find matched keywords
            job_keywords = set(self.required_skills + self.preferred_skills)
            matched_keywords = [kw for kw in job_keywords if kw in resume_text.lower()]
            
            return {
                'compatibility_score': round(similarity, 4),
                'similarity_score': round(similarity, 4),
                'matched_keywords': matched_keywords
            }
            
        except Exception as e:
            logger.error(f"Error calculating resume compatibility: {e}")
            return {
                'compatibility_score': 0.0,
                'similarity_score': 0.0,
                'matched_keywords': [],
                'error': str(e)
            }
    
    def calculate_final_score(
        self,
        github_linkedin_score: float,
        resume_score: float,
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Calculate final averaged leaderboard score
        
        Args:
            github_linkedin_score: Compatibility score from GitHub/LinkedIn (0-1)
            resume_score: Compatibility score from resume (0-1)
            weights: Optional custom weights for averaging
                     Default: {'github_linkedin': 0.5, 'resume': 0.5}
        
        Returns:
            Dictionary containing:
                - final_score: Averaged score (0-1)
                - normalized_score: Score on 0-100 scale
                - github_linkedin_score: Input GitHub/LinkedIn score
                - resume_score: Input resume score
                - weights_used: Weights applied
                - tier: Performance tier (Excellent/Good/Fair/Poor)
        """
        # Default equal weighting
        if weights is None:
            weights = {'github_linkedin': 0.5, 'resume': 0.5}
        
        # Ensure weights sum to 1.0
        total_weight = weights['github_linkedin'] + weights['resume']
        if total_weight != 1.0:
            weights = {
                'github_linkedin': weights['github_linkedin'] / total_weight,
                'resume': weights['resume'] / total_weight
            }
        
        # Calculate weighted average
        final_score = (
            github_linkedin_score * weights['github_linkedin'] +
            resume_score * weights['resume']
        )
        
        # Normalize to 0-100 scale
        normalized_score = final_score * 100
        
        # Determine tier
        if normalized_score >= 80:
            tier = 'Excellent'
            emoji = '🌟'
        elif normalized_score >= 65:
            tier = 'Good'
            emoji = '✅'
        elif normalized_score >= 50:
            tier = 'Fair'
            emoji = '👍'
        else:
            tier = 'Poor'
            emoji = '⚠️'
        
        return {
            'final_score': round(final_score, 4),
            'normalized_score': round(normalized_score, 2),
            'github_linkedin_score': round(github_linkedin_score, 4),
            'resume_score': round(resume_score, 4),
            'weights_used': weights,
            'tier': tier,
            'emoji': emoji
        }


class CandidateScorer:
    """
    Complete candidate scoring system integrating all data sources
    """
    
    def __init__(self, job_description: Dict[str, Any]):
        """
        Initialize candidate scorer
        
        Args:
            job_description: Job description and requirements
        """
        self.compatibility_scorer = CompatibilityScorer(job_description)
        self.job_description = job_description
        logger.info("Initialized CandidateScorer")
    
    def score_candidate(
        self,
        candidate_name: str,
        resume_text: Optional[str] = None,
        github_analysis: Optional[Dict[str, Any]] = None,
        linkedin_data: Optional[Dict[str, Any]] = None,
        candidate_skills: Optional[Dict[str, Any]] = None,
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Score a candidate using all available data sources
        
        Args:
            candidate_name: Candidate's name
            resume_text: Resume text (optional)
            github_analysis: GitHub analysis results (optional)
            linkedin_data: LinkedIn profile data (optional)
            candidate_skills: Simplified skills dict with 'github' and 'linkedin' keys (optional)
            weights: Custom scoring weights (optional)
        
        Returns:
            Complete scoring results with final averaged score
        """
        results = {
            'candidate_name': candidate_name,
            'timestamp': None
        }
        
        # Calculate GitHub/LinkedIn compatibility
        github_linkedin_compatibility = None
        if github_analysis or linkedin_data or candidate_skills:
            if candidate_skills is None:
                candidate_skills = {}
            
            github_linkedin_compatibility = self.compatibility_scorer.calculate_github_linkedin_compatibility(
                candidate_skills=candidate_skills,
                github_analysis=github_analysis,
                linkedin_data=linkedin_data
            )
            results['github_linkedin_compatibility'] = github_linkedin_compatibility
        else:
            results['github_linkedin_compatibility'] = None
        
        # Calculate resume compatibility
        resume_compatibility = None
        if resume_text:
            resume_compatibility = self.compatibility_scorer.calculate_resume_compatibility(resume_text)
            results['resume_compatibility'] = resume_compatibility
        else:
            results['resume_compatibility'] = None
        
        # Calculate final score if we have both scores
        if github_linkedin_compatibility and resume_compatibility:
            final_score = self.compatibility_scorer.calculate_final_score(
                github_linkedin_score=github_linkedin_compatibility['compatibility_score'],
                resume_score=resume_compatibility['compatibility_score'],
                weights=weights
            )
            results['final_score_data'] = final_score
            results['final_score'] = final_score['final_score']
            results['normalized_score'] = final_score['normalized_score']
            results['tier'] = final_score['tier']
        elif github_linkedin_compatibility:
            # Only GitHub/LinkedIn data available
            score = github_linkedin_compatibility['compatibility_score']
            results['final_score'] = score
            results['normalized_score'] = score * 100
            results['tier'] = 'Good' if score >= 0.65 else 'Fair' if score >= 0.5 else 'Poor'
        elif resume_compatibility:
            # Only resume data available
            score = resume_compatibility['compatibility_score']
            results['final_score'] = score
            results['normalized_score'] = score * 100
            results['tier'] = 'Good' if score >= 0.65 else 'Fair' if score >= 0.5 else 'Poor'
        else:
            # No data available
            results['final_score'] = 0.0
            results['normalized_score'] = 0.0
            results['tier'] = 'No Data'
            results['error'] = 'No candidate data provided'
        
        return results
    
    def score_multiple_candidates(
        self,
        candidates: List[Dict[str, Any]],
        weights: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Score multiple candidates and generate leaderboard
        
        Args:
            candidates: List of candidate dictionaries, each containing:
                - name: Candidate name
                - resume_text: Resume text (optional)
                - github_analysis: GitHub analysis (optional)
                - linkedin_data: LinkedIn data (optional)
                - candidate_skills: Skills dict (optional)
            weights: Custom scoring weights (optional)
        
        Returns:
            Sorted list of candidates with scores (highest to lowest)
        """
        scored_candidates = []
        
        for candidate in candidates:
            try:
                score_result = self.score_candidate(
                    candidate_name=candidate.get('name', 'Unknown'),
                    resume_text=candidate.get('resume_text'),
                    github_analysis=candidate.get('github_analysis'),
                    linkedin_data=candidate.get('linkedin_data'),
                    candidate_skills=candidate.get('candidate_skills'),
                    weights=weights
                )
                scored_candidates.append(score_result)
            except Exception as e:
                logger.error(f"Error scoring candidate {candidate.get('name', 'Unknown')}: {e}")
                continue
        
        # Sort by final score (descending)
        scored_candidates.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        
        # Add ranks
        for rank, candidate in enumerate(scored_candidates, start=1):
            candidate['rank'] = rank
        
        logger.info(f"Scored and ranked {len(scored_candidates)} candidates")
        
        return scored_candidates


# Example usage
if __name__ == "__main__":
    # Example job description
    job_desc = {
        'role': 'Backend Developer',
        'required_skills': ['Python', 'Django', 'PostgreSQL', 'REST API'],
        'preferred_skills': ['Docker', 'AWS', 'Redis'],
        'description': 'We are looking for an experienced backend developer to build scalable APIs',
        'experience': '3+ years'
    }
    
    # Initialize scorer
    scorer = CandidateScorer(job_desc)
    
    # Example candidate data
    candidate = {
        'name': 'John Doe',
        'resume_text': 'Experienced Python developer with Django and PostgreSQL. Built REST APIs.',
        'candidate_skills': {
            'github': ['Python', 'Django', 'Docker', 'Git'],
            'linkedin': ['Python', 'PostgreSQL', 'AWS', 'Team Leadership']
        }
    }
    
    # Score candidate
    result = scorer.score_candidate(
        candidate_name=candidate['name'],
        resume_text=candidate['resume_text'],
        candidate_skills=candidate['candidate_skills']
    )
    
    print(json.dumps(result, indent=2))
