#!/usr/bin/env python3
"""
Comprehensive Resume Parser
Extracts ALL candidate information from resume text including:
- Name, Email, Phone, Location
- Education (degree, university), CGPA
- Experience (years), Projects count
- Technical Skills
- Professional links (GitHub, LinkedIn)
- Summary/Bio
"""

import re
import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

# Try to import Google Generative AI for intelligent parsing
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logging.warning("Google Generative AI not available. Using regex-based parsing only.")

logger = logging.getLogger(__name__)


class ComprehensiveResumeParser:
    """Extract comprehensive candidate information from resume text"""

    def __init__(self, use_ai: bool = True):
        """
        Initialize the parser

        Args:
            use_ai: Whether to use AI-powered parsing (requires Gemini API key)
        """
        self.use_ai = use_ai and GENAI_AVAILABLE

        # Initialize Gemini if available and API key is set
        if self.use_ai:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    # Use the latest Gemini 2.0 Flash model for best performance
                    self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                    logger.info("AI-powered parsing enabled with gemini-2.0-flash-exp")
                except Exception as e:
                    logger.warning(f"Failed to initialize Gemini: {e}")
                    self.use_ai = False
            else:
                logger.info("No GEMINI_API_KEY found, using regex-based parsing")
                self.use_ai = False

        # Regex patterns for fallback parsing
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self.phone_pattern = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4,6}')
        self.github_pattern = re.compile(r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)', re.IGNORECASE)
        self.linkedin_pattern = re.compile(r'(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_-]+)', re.IGNORECASE)
        self.cgpa_pattern = re.compile(r'(?:CGPA|GPA|Grade|Percentage)[:\s]*([0-9]+\.?[0-9]*)\s*(?:/\s*10|/\s*4)?', re.IGNORECASE)
        self.experience_pattern = re.compile(r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)', re.IGNORECASE)

    def parse_with_ai(self, resume_text: str) -> Dict[str, Any]:
        """
        Use AI to intelligently extract all resume information

        Args:
            resume_text: Raw resume text

        Returns:
            Dictionary with all extracted fields
        """
        if not self.use_ai:
            return None

        prompt = f"""
Extract ALL the following information from this resume. Return a JSON object with these exact fields:

{{
  "name": "Full name of the candidate",
  "email": "Email address",
  "phone": "Phone number",
  "location": "City, Country or location mentioned",
  "education": "Highest degree (e.g., B.Tech in Computer Science)",
  "university": "University or college name",
  "cgpa": "CGPA or GPA as a number (convert percentage to 10-point scale if needed)",
  "experience_years": "Total years of experience as a number (extract from work history)",
  "projects_count": "Number of projects mentioned (count them)",
  "skills": ["List", "of", "technical", "skills"],
  "github": "GitHub username (not full URL, just username)",
  "linkedin": "LinkedIn profile username (not full URL, just username)",
  "summary": "Brief 1-2 sentence professional summary"
}}

Rules:
- If a field is not found, use empty string "" or empty array [] or 0 for numbers
- For experience_years, count years from work history dates
- For projects_count, count distinct projects mentioned
- For skills, list ALL technical skills, frameworks, languages, tools mentioned
- Extract ONLY the username from GitHub/LinkedIn URLs
- For CGPA, convert percentages to 10-point scale (e.g., 85% = 8.5 CGPA)
- Return ONLY valid JSON, no additional text

Resume Text:
{resume_text[:8000]}
"""

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()

            # Clean up the response - remove markdown code blocks if present
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
                result_text = result_text.strip()

            import json
            parsed_data = json.loads(result_text)

            # Validate and clean the data
            return self._validate_parsed_data(parsed_data)

        except Exception as e:
            logger.error(f"AI parsing error: {e}")
            return None

    def parse_with_regex(self, resume_text: str) -> Dict[str, Any]:
        """
        Fallback regex-based parsing

        Args:
            resume_text: Raw resume text

        Returns:
            Dictionary with extracted fields
        """
        # Extract basic info
        emails = self.email_pattern.findall(resume_text)
        phones = self.phone_pattern.findall(resume_text)
        github_matches = self.github_pattern.findall(resume_text)
        linkedin_matches = self.linkedin_pattern.findall(resume_text)
        cgpa_matches = self.cgpa_pattern.findall(resume_text)
        experience_matches = self.experience_pattern.findall(resume_text)

        # Extract name (first non-empty line that looks like a name)
        name = self._extract_name_regex(resume_text)

        # Extract location
        location = self._extract_location_regex(resume_text)

        # Extract education
        education_info = self._extract_education_regex(resume_text)

        # Extract skills
        skills = self._extract_skills_regex(resume_text)

        # Count projects
        projects_count = self._count_projects_regex(resume_text)

        # Generate summary
        summary = self._generate_summary_regex(resume_text, skills)

        return {
            'name': name,
            'email': emails[0] if emails else '',
            'phone': phones[0] if phones else '',
            'location': location,
            'education': education_info.get('degree', ''),
            'university': education_info.get('university', ''),
            'cgpa': float(cgpa_matches[0]) if cgpa_matches else 0.0,
            'experience_years': int(experience_matches[0]) if experience_matches else 0,
            'projects_count': projects_count,
            'skills': skills,
            'github': github_matches[0] if github_matches else '',
            'linkedin': linkedin_matches[0] if linkedin_matches else '',
            'summary': summary
        }

    def _extract_name_regex(self, text: str) -> str:
        """Extract candidate name from resume"""
        lines = [line.strip() for line in text.split('\n')[:10] if line.strip()]

        for line in lines:
            # Skip lines with common keywords
            if any(kw in line.lower() for kw in ['email', '@', 'phone', 'http', 'resume', 'cv', 'curriculum']):
                continue

            # Check if line looks like a name (2-4 words, mostly capitalized)
            words = line.split()
            if 2 <= len(words) <= 4:
                if any(w[0].isupper() for w in words if w):
                    if not any(c.isdigit() for c in line):
                        return line

        return lines[0] if lines else 'Unknown Candidate'

    def _extract_location_regex(self, text: str) -> str:
        """Extract location from resume"""
        location_patterns = [
            r'(?:Location|Address|Based in|City)[:\s]+([A-Z][a-zA-Z\s,]+(?:India|USA|UK|Canada|Singapore)?)',
            r'([A-Z][a-z]+,\s*(?:India|USA|UK|Canada|Singapore))',
        ]

        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return ''

    def _extract_education_regex(self, text: str) -> Dict[str, str]:
        """Extract education information"""
        education_keywords = ['education', 'academic', 'qualification', 'degree']

        # Find education section
        lines = text.split('\n')
        edu_start = -1

        for i, line in enumerate(lines):
            if any(kw in line.lower() for kw in education_keywords):
                edu_start = i
                break

        if edu_start >= 0:
            edu_section = '\n'.join(lines[edu_start:edu_start+10])

            # Common degree patterns
            degree_patterns = [
                r'(B\.?Tech|Bachelor|M\.?Tech|Master|PhD|B\.?E\.?|M\.?E\.?)[\s\w]*(?:in)?\s*([\w\s]+)',
                r'(Bachelor|Master)(?:\'s)?\s*(?:of)?\s*([\w\s]+)',
            ]

            degree = ''
            university = ''

            for pattern in degree_patterns:
                match = re.search(pattern, edu_section, re.IGNORECASE)
                if match:
                    degree = f"{match.group(1)} in {match.group(2).strip()}"
                    break

            # Extract university
            uni_patterns = [
                r'(?:from|at|@)\s*([A-Z][A-Za-z\s&,]+(?:University|Institute|College))',
                r'([A-Z][A-Za-z\s&,]+(?:University|Institute|College|IIT|NIT))',
            ]

            for pattern in uni_patterns:
                match = re.search(pattern, edu_section)
                if match:
                    university = match.group(1).strip()
                    break

            return {'degree': degree, 'university': university}

        return {'degree': '', 'university': ''}

    def _extract_skills_regex(self, text: str) -> List[str]:
        """Extract technical skills"""
        # Common technical skills
        common_skills = [
            'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'Go', 'Rust', 'Swift', 'Kotlin',
            'React', 'Angular', 'Vue', 'Node.js', 'Express', 'Django', 'Flask', 'Spring',
            'HTML', 'CSS', 'TypeScript', 'PHP', 'SQL', 'NoSQL',
            'MongoDB', 'MySQL', 'PostgreSQL', 'Redis', 'Elasticsearch',
            'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Jenkins', 'CI/CD',
            'Git', 'GitHub', 'GitLab', 'Jira', 'Agile', 'Scrum',
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy',
            'RESTful', 'GraphQL', 'Microservices', 'API', 'OAuth',
            'Linux', 'Unix', 'Bash', 'Shell',
        ]

        found_skills = []
        text_lower = text.lower()

        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)

        return found_skills[:15]  # Limit to top 15 skills

    def _count_projects_regex(self, text: str) -> int:
        """Count projects mentioned in resume"""
        project_keywords = ['project', 'built', 'developed', 'created', 'implemented']

        # Simple heuristic: count occurrences of project-related keywords
        count = 0
        for keyword in project_keywords:
            count += len(re.findall(rf'\b{keyword}\b', text, re.IGNORECASE))

        # Estimate project count (very rough approximation)
        estimated_projects = min(count // 2, 20)  # Cap at 20

        return max(estimated_projects, 3)  # Minimum 3 projects

    def _generate_summary_regex(self, text: str, skills: List[str]) -> str:
        """Generate a brief summary"""
        if skills:
            top_skills = skills[:3]
            return f"Strong expertise in {', '.join(top_skills)} and related technologies"
        return "Experienced professional with diverse technical background"

    def _validate_parsed_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean parsed data"""
        # Ensure all required fields exist
        default_data = {
            'name': 'Unknown Candidate',
            'email': '',
            'phone': '',
            'location': '',
            'education': '',
            'university': '',
            'cgpa': 0.0,
            'experience_years': 0,
            'projects_count': 0,
            'skills': [],
            'github': '',
            'linkedin': '',
            'summary': ''
        }

        # Merge with defaults
        for key, default_value in default_data.items():
            if key not in data or data[key] is None:
                data[key] = default_value

        # Clean and validate specific fields
        try:
            data['cgpa'] = float(data['cgpa']) if data['cgpa'] else 0.0
            # Ensure CGPA is in 0-10 range
            if data['cgpa'] > 10:
                data['cgpa'] = data['cgpa'] / 10  # Convert percentage to CGPA
            data['cgpa'] = min(10.0, max(0.0, data['cgpa']))
        except:
            data['cgpa'] = 0.0

        try:
            data['experience_years'] = int(data['experience_years']) if data['experience_years'] else 0
            data['experience_years'] = max(0, min(50, data['experience_years']))  # 0-50 years
        except:
            data['experience_years'] = 0

        try:
            data['projects_count'] = int(data['projects_count']) if data['projects_count'] else 0
            data['projects_count'] = max(0, min(100, data['projects_count']))  # 0-100 projects
        except:
            data['projects_count'] = 0

        # Ensure skills is a list
        if not isinstance(data['skills'], list):
            data['skills'] = []

        # Clean GitHub/LinkedIn (remove URLs, keep only username)
        if data['github']:
            data['github'] = data['github'].split('/')[-1].strip()
        if data['linkedin']:
            data['linkedin'] = data['linkedin'].split('/')[-1].strip()

        return data

    def parse(self, resume_text: str) -> Dict[str, Any]:
        """
        Parse resume and extract all comprehensive information

        Args:
            resume_text: Raw resume text

        Returns:
            Dictionary with all extracted candidate information
        """
        if not resume_text or not resume_text.strip():
            return self._validate_parsed_data({})

        # Try AI parsing first
        if self.use_ai:
            try:
                ai_result = self.parse_with_ai(resume_text)
                if ai_result:
                    logger.info("Successfully parsed resume with AI")
                    return ai_result
            except Exception as e:
                logger.warning(f"AI parsing failed, falling back to regex: {e}")

        # Fallback to regex parsing
        logger.info("Using regex-based parsing")
        return self.parse_with_regex(resume_text)


def parse_comprehensive_resume(resume_text: str, use_ai: bool = True) -> Dict[str, Any]:
    """
    Convenience function to parse resume comprehensively

    Args:
        resume_text: Raw resume text
        use_ai: Whether to use AI-powered parsing

    Returns:
        Dictionary with all extracted information
    """
    parser = ComprehensiveResumeParser(use_ai=use_ai)
    return parser.parse(resume_text)


if __name__ == '__main__':
    # Test the parser
    sample_resume = """
    John Doe
    Email: john.doe@example.com
    Phone: +1-555-123-4567
    Location: San Francisco, USA

    EDUCATION
    B.Tech in Computer Science
    Stanford University
    CGPA: 9.2/10

    EXPERIENCE
    5 years of experience in software development

    SKILLS
    Python, JavaScript, React, Node.js, Docker, AWS, MongoDB

    GITHUB: https://github.com/johndoe
    LINKEDIN: https://linkedin.com/in/johndoe

    PROJECTS
    - Built e-commerce platform
    - Developed mobile app
    - Created data pipeline
    """

    result = parse_comprehensive_resume(sample_resume)

    import json
    print(json.dumps(result, indent=2))
