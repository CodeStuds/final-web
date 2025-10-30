#!/usr/bin/env python3
"""
Resume URL Extractor
Extracts GitHub and LinkedIn URLs from resume text
"""

import re
import logging
from typing import Dict, Optional, List
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ResumeURLExtractor:
    """
    Extracts social profile URLs from resume text
    Supports GitHub, LinkedIn, and other platforms
    """
    
    def __init__(self):
        """Initialize URL extractor with regex patterns"""
        
        # GitHub URL patterns
        self.github_patterns = [
            r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?)',
            r'github\.com/([a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?)',
            r'@([a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?)\s+(?:on|at)\s+github',
        ]
        
        # LinkedIn URL patterns
        self.linkedin_patterns = [
            r'(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9-]+)',
            r'linkedin\.com/in/([a-zA-Z0-9-]+)',
            r'in\.linkedin\.com/in/([a-zA-Z0-9-]+)',
        ]
        
        # General URL pattern for validation
        self.url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    
    def extract_github_info(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract GitHub username and URL from text
        
        Args:
            text: Resume text
        
        Returns:
            Dictionary with:
                - username: GitHub username (or None)
                - url: Full GitHub URL (or None)
                - found: Boolean indicating if GitHub profile was found
        """
        if not text:
            return {'username': None, 'url': None, 'found': False}
        
        text_lower = text.lower()
        
        # Try each GitHub pattern
        for pattern in self.github_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                username = match.group(1)
                
                # Validate username (GitHub rules)
                if self._is_valid_github_username(username):
                    url = f"https://github.com/{username}"
                    logger.info(f"Found GitHub profile: {url}")
                    return {
                        'username': username,
                        'url': url,
                        'found': True
                    }
        
        logger.info("No GitHub profile found in resume")
        return {'username': None, 'url': None, 'found': False}
    
    def extract_linkedin_info(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract LinkedIn profile URL from text
        
        Args:
            text: Resume text
        
        Returns:
            Dictionary with:
                - profile_id: LinkedIn profile ID (or None)
                - url: Full LinkedIn URL (or None)
                - found: Boolean indicating if LinkedIn profile was found
        """
        if not text:
            return {'profile_id': None, 'url': None, 'found': False}
        
        # Try each LinkedIn pattern
        for pattern in self.linkedin_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                profile_id = match.group(1)
                
                # Validate profile ID
                if self._is_valid_linkedin_profile_id(profile_id):
                    url = f"https://linkedin.com/in/{profile_id}"
                    logger.info(f"Found LinkedIn profile: {url}")
                    return {
                        'profile_id': profile_id,
                        'url': url,
                        'found': True
                    }
        
        logger.info("No LinkedIn profile found in resume")
        return {'profile_id': None, 'url': None, 'found': False}
    
    def extract_all_urls(self, text: str) -> List[str]:
        """
        Extract all URLs from text
        
        Args:
            text: Resume text
        
        Returns:
            List of all URLs found
        """
        if not text:
            return []
        
        urls = re.findall(self.url_pattern, text)
        return list(set(urls))  # Remove duplicates
    
    def extract_all_profiles(self, text: str) -> Dict[str, Dict]:
        """
        Extract all social profile information from text
        
        Args:
            text: Resume text
        
        Returns:
            Dictionary with GitHub, LinkedIn, and other profile info
        """
        result = {
            'github': self.extract_github_info(text),
            'linkedin': self.extract_linkedin_info(text),
            'all_urls': self.extract_all_urls(text)
        }
        
        # Add other social platforms
        result['other_profiles'] = self._extract_other_profiles(text)
        
        return result
    
    def _is_valid_github_username(self, username: str) -> bool:
        """
        Validate GitHub username
        
        Rules:
        - 1-39 characters
        - Alphanumeric and hyphens
        - Cannot start or end with hyphen
        """
        if not username or len(username) > 39:
            return False
        
        # Check pattern
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$'
        return bool(re.match(pattern, username))
    
    def _is_valid_linkedin_profile_id(self, profile_id: str) -> bool:
        """
        Validate LinkedIn profile ID
        
        Rules:
        - 3-100 characters
        - Alphanumeric and hyphens
        - Not just numbers (to avoid false positives)
        """
        if not profile_id or len(profile_id) < 3 or len(profile_id) > 100:
            return False
        
        # Must contain at least one letter (not just numbers)
        if not re.search(r'[a-zA-Z]', profile_id):
            return False
        
        # Valid characters: alphanumeric and hyphens
        pattern = r'^[a-zA-Z0-9-]+$'
        return bool(re.match(pattern, profile_id))
    
    def _extract_other_profiles(self, text: str) -> Dict[str, List[str]]:
        """
        Extract other social platform URLs
        
        Args:
            text: Resume text
        
        Returns:
            Dictionary with lists of URLs for each platform
        """
        platforms = {
            'twitter': r'(?:https?://)?(?:www\.)?twitter\.com/([a-zA-Z0-9_]+)',
            'stackoverflow': r'(?:https?://)?stackoverflow\.com/users/(\d+)',
            'gitlab': r'(?:https?://)?(?:www\.)?gitlab\.com/([a-zA-Z0-9-_]+)',
            'bitbucket': r'(?:https?://)?bitbucket\.org/([a-zA-Z0-9-_]+)',
            'medium': r'(?:https?://)?(?:www\.)?medium\.com/@([a-zA-Z0-9-_]+)',
            'dev.to': r'(?:https?://)?dev\.to/([a-zA-Z0-9-_]+)',
            'portfolio': r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.(?:com|io|dev|me|tech))',
        }
        
        result = {}
        for platform, pattern in platforms.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                result[platform] = list(set(matches))
        
        return result
    
    def extract_email(self, text: str) -> Optional[str]:
        """
        Extract email address from text
        
        Args:
            text: Resume text
        
        Returns:
            Email address or None
        """
        if not text:
            return None
        
        # Email pattern
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(pattern, text)
        
        if matches:
            # Return first email found
            email = matches[0]
            logger.info(f"Found email: {email}")
            return email
        
        return None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """
        Extract phone number from text
        
        Args:
            text: Resume text
        
        Returns:
            Phone number or None
        """
        if not text:
            return None
        
        # Phone patterns (various formats)
        patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # +1-234-567-8900
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (234) 567-8900
            r'\d{10}',  # 2345678900
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                phone = matches[0]
                logger.info(f"Found phone: {phone}")
                return phone
        
        return None
    
    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract all contact information from text
        
        Args:
            text: Resume text
        
        Returns:
            Dictionary with email, phone, GitHub, LinkedIn, etc.
        """
        profiles = self.extract_all_profiles(text)
        
        return {
            'email': self.extract_email(text),
            'phone': self.extract_phone(text),
            'github_username': profiles['github']['username'],
            'github_url': profiles['github']['url'],
            'linkedin_profile_id': profiles['linkedin']['profile_id'],
            'linkedin_url': profiles['linkedin']['url'],
            'other_profiles': profiles['other_profiles'],
            'all_urls': profiles['all_urls']
        }


# Convenience functions
def extract_github_username(text: str) -> Optional[str]:
    """
    Quick function to extract GitHub username from text
    
    Args:
        text: Resume text
    
    Returns:
        GitHub username or None
    """
    extractor = ResumeURLExtractor()
    result = extractor.extract_github_info(text)
    return result['username']


def extract_linkedin_profile(text: str) -> Optional[str]:
    """
    Quick function to extract LinkedIn profile ID from text
    
    Args:
        text: Resume text
    
    Returns:
        LinkedIn profile ID or None
    """
    extractor = ResumeURLExtractor()
    result = extractor.extract_linkedin_info(text)
    return result['profile_id']


def extract_all_contact_info(text: str) -> Dict:
    """
    Quick function to extract all contact information
    
    Args:
        text: Resume text
    
    Returns:
        Dictionary with all contact info
    """
    extractor = ResumeURLExtractor()
    return extractor.extract_contact_info(text)


# Example usage
if __name__ == "__main__":
    # Example resume text
    resume_text = """
    John Doe
    Email: johndoe@example.com
    Phone: (555) 123-4567
    GitHub: https://github.com/johndoe
    LinkedIn: https://linkedin.com/in/john-doe-developer
    
    Experienced Python developer with 5 years of experience.
    Check out my portfolio at https://johndoe.dev
    
    Skills: Python, Django, React, Node.js
    """
    
    print("=" * 70)
    print("RESUME URL EXTRACTOR - EXAMPLE")
    print("=" * 70)
    
    extractor = ResumeURLExtractor()
    
    # Extract all contact info
    contact_info = extractor.extract_contact_info(resume_text)
    
    print("\n📧 Contact Information:")
    print(f"   Email: {contact_info['email']}")
    print(f"   Phone: {contact_info['phone']}")
    
    print("\n💻 GitHub:")
    print(f"   Username: {contact_info['github_username']}")
    print(f"   URL: {contact_info['github_url']}")
    
    print("\n👔 LinkedIn:")
    print(f"   Profile ID: {contact_info['linkedin_profile_id']}")
    print(f"   URL: {contact_info['linkedin_url']}")
    
    print("\n🌐 Other Profiles:")
    for platform, profiles in contact_info['other_profiles'].items():
        print(f"   {platform.title()}: {', '.join(profiles)}")
    
    print("\n🔗 All URLs Found:")
    for url in contact_info['all_urls']:
        print(f"   - {url}")
    
    print("\n" + "=" * 70)
