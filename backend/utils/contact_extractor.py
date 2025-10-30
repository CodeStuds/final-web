#!/usr/bin/env python3
"""
Email and Contact Extractor Utility
Extracts emails, phone numbers, LinkedIn and GitHub URLs from text
Converted from Colab script to standalone utility
"""

import re
from typing import Dict, List, Optional


class ContactExtractor:
    """Extract contact information from resume text"""
    
    def __init__(self):
        """Initialize regex patterns"""
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self.phone_pattern = re.compile(r'(?:(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4,6})')
        self.linkedin_pattern = re.compile(r'(https?://(www\.)?linkedin\.com/[a-zA-Z0-9_/.\-]+)')
        self.github_pattern = re.compile(r'(https?://(www\.)?github\.com/[a-zA-Z0-9_/.\-]+)')
    
    def extract_from_text(self, text: str) -> Dict[str, List[str]]:
        """
        Extract all contact information from text
        
        Args:
            text: Resume text content
            
        Returns:
            Dictionary with emails, phones, linkedin, github URLs
        """
        # Extract and deduplicate while preserving order
        emails = list(dict.fromkeys(self.email_pattern.findall(text)))
        phones = list(dict.fromkeys(self.phone_pattern.findall(text)))
        linkedins = list(dict.fromkeys([match[0] for match in self.linkedin_pattern.findall(text)]))
        githubs = list(dict.fromkeys([match[0] for match in self.github_pattern.findall(text)]))
        
        return {
            'emails': emails,
            'phones': phones,
            'linkedin': linkedins,
            'github': githubs
        }
    
    def extract_from_file(self, file_path: str) -> Dict[str, List[str]]:
        """
        Extract contact information from a text file
        
        Args:
            file_path: Path to text file
            
        Returns:
            Dictionary with contact information
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            return self.extract_from_text(text)
        except Exception as e:
            return {
                'emails': [],
                'phones': [],
                'linkedin': [],
                'github': [],
                'error': str(e)
            }


def extract_contacts(text: str) -> Dict[str, List[str]]:
    """
    Convenience function to extract contacts from text
    
    Args:
        text: Resume text
        
    Returns:
        Dictionary with contact information
    """
    extractor = ContactExtractor()
    return extractor.extract_from_text(text)


if __name__ == '__main__':
    # Example usage
    sample_text = """
    John Doe
    Email: john.doe@example.com
    Phone: +1-555-123-4567
    LinkedIn: https://www.linkedin.com/in/johndoe
    GitHub: https://github.com/johndoe
    """
    
    contacts = extract_contacts(sample_text)
    print("Extracted contacts:")
    for key, values in contacts.items():
        print(f"  {key}: {values}")
