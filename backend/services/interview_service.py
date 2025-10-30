#!/usr/bin/env python3
"""
Interview Question Generation Service
Consolidated interview question generation using Gemini API
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


class InterviewService:
    """
    Unified interview question generation service using Google Gemini API
    """
    
    DEFAULT_MODEL = "gemini-2.0-flash-exp"
    API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Interview Service
        
        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        
        if not self.api_key:
            logger.warning("No Gemini API key provided. Service will not be functional.")
    
    def validate_api_key(self) -> bool:
        """
        Check if API key is configured
        
        Returns:
            bool: True if API key is available
        """
        return bool(self.api_key)
    
    def generate_questions(
        self,
        candidate_name: str,
        candidate_profile: str,
        model: Optional[str] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Generate personalized interview questions for a candidate
        
        Args:
            candidate_name: Name of the candidate
            candidate_profile: Combined text from GitHub/LinkedIn profiles
            model: Optional Gemini model to use (defaults to DEFAULT_MODEL)
            timeout: Request timeout in seconds
            
        Returns:
            dict: Generated interview questions and metadata
            
        Raises:
            ValueError: If API key is not configured or profile is empty
            RuntimeError: If API request fails
        """
        if not self.validate_api_key():
            raise ValueError(
                "Gemini API key not configured. Set GEMINI_API_KEY environment variable."
            )
        
        if not candidate_profile or not candidate_profile.strip():
            raise ValueError("Candidate profile cannot be empty")
        
        model = model or self.DEFAULT_MODEL
        
        # Build prompt
        prompt = self._build_prompt(candidate_name, candidate_profile)
        
        try:
            # Call Gemini API
            logger.info(f"Generating interview questions for: {candidate_name}")
            
            url = self.API_ENDPOINT.format(model=model)
            response = requests.post(
                f"{url}?key={self.api_key}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=timeout
            )
            
            if response.status_code != 200:
                error_msg = f"Gemini API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            result = response.json()
            questions_text = result["candidates"][0]["content"]["parts"][0]["text"]
            
            return {
                'success': True,
                'candidate_name': candidate_name,
                'interview_questions': questions_text,
                'model': model,
                'timestamp': datetime.now().isoformat()
            }
            
        except requests.exceptions.Timeout:
            raise RuntimeError(f"Request timed out after {timeout} seconds")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API request failed: {str(e)}")
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Unexpected API response format: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating questions for {candidate_name}: {e}")
            raise RuntimeError(f"Question generation failed: {str(e)}")
    
    def batch_generate(
        self,
        candidates: List[Dict[str, str]],
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate interview questions for multiple candidates
        
        Args:
            candidates: List of dicts with 'name' and 'profile' keys
            model: Optional Gemini model to use
            
        Returns:
            dict: Batch generation results with success/failure for each candidate
        """
        results = []
        errors = []
        
        for candidate in candidates:
            candidate_name = candidate.get('name', 'Unknown')
            candidate_profile = candidate.get('profile', '')
            
            try:
                result = self.generate_questions(
                    candidate_name,
                    candidate_profile,
                    model
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to generate questions for {candidate_name}: {e}")
                errors.append({
                    'candidate_name': candidate_name,
                    'error': str(e)
                })
        
        return {
            'success': True,
            'total': len(candidates),
            'successful': len(results),
            'failed': len(errors),
            'results': results,
            'errors': errors,
            'timestamp': datetime.now().isoformat()
        }
    
    def _build_prompt(self, candidate_name: str, candidate_profile: str) -> str:
        """
        Build prompt for interview question generation
        
        Args:
            candidate_name: Candidate's name
            candidate_profile: Candidate's profile text
            
        Returns:
            str: Formatted prompt
        """
        # Limit profile length to avoid token limits
        max_profile_length = 5000
        truncated_profile = candidate_profile[:max_profile_length]
        if len(candidate_profile) > max_profile_length:
            truncated_profile += "\n... (profile truncated)"
        
        return f"""
You are an expert technical interviewer and HR assistant.

You will receive a candidate profile containing combined text from their GitHub and LinkedIn profiles — including project details, skills, experiences, and technical achievements.

Generate a comprehensive interview guide with:
1. A 3-4 line thesis summary of the candidate's expertise
2. 8-10 technical questions based on their projects and skills (make them specific to the candidate's work)
3. 3-5 behavioral/HR questions
4. 2-3 follow-up questions connecting their technical work to real-world use cases

Make questions personalized and specific to this candidate. Focus on depth over breadth.

Candidate: {candidate_name}

Profile:
{truncated_profile}

Please format the output clearly with section headers.
"""
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Check if interview service is available
        
        Returns:
            dict: Service status information
        """
        return {
            'service': 'interview',
            'available': self.validate_api_key(),
            'has_api_key': self.validate_api_key(),
            'default_model': self.DEFAULT_MODEL
        }


def create_interview_service(api_key: Optional[str] = None) -> InterviewService:
    """
    Factory function to create Interview service instance
    
    Args:
        api_key: Optional Gemini API key
        
    Returns:
        InterviewService instance
    """
    return InterviewService(api_key)
