#!/usr/bin/env python3
"""
Resume Text Extraction Utility
Extracts text from PDF, DOCX, DOC, and TXT files
Converted from Colab script to standalone utility
"""

import os
from pathlib import Path
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

# Optional imports - gracefully handle if not available
try:
    import pdfplumber
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logger.warning("PyPDF2 or pdfplumber not available. PDF extraction disabled.")

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logger.warning("python-docx not available. DOCX extraction disabled.")


class ResumeTextExtractor:
    """Extract text from various resume file formats"""
    
    def __init__(self):
        """Initialize the extractor"""
        self.supported_formats = {'.txt', '.pdf', '.docx', '.doc'}
    
    def extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using pdfplumber first, fallback to PyPDF2"""
        if not PYPDF2_AVAILABLE:
            return ""
        
        text = ""
        
        # Try pdfplumber first (better layout preservation)
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.debug(f"pdfplumber failed for {file_path}: {e}")
        
        # Fallback to PyPDF2 if no text extracted
        if not text.strip():
            try:
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e:
                logger.error(f"PyPDF2 error for {file_path}: {e}")
        
        return text.strip()
    
    def extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        if not DOCX_AVAILABLE:
            return ""
        
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            logger.error(f"DOCX extraction error for {file_path}: {e}")
            return ""
    
    def extract_from_txt(self, file_path: str) -> str:
        """Extract text from plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"TXT extraction error for {file_path}: {e}")
            return ""
    
    def extract_text(self, file_path: str) -> Dict[str, any]:
        """
        Extract text from any supported file format
        
        Args:
            file_path: Path to resume file
            
        Returns:
            Dictionary with:
                - success: bool
                - text: extracted text
                - format: file format
                - error: error message if failed
        """
        path = Path(file_path)
        
        if not path.exists():
            return {
                'success': False,
                'text': '',
                'format': None,
                'error': 'File not found'
            }
        
        file_ext = path.suffix.lower()
        
        if file_ext not in self.supported_formats:
            return {
                'success': False,
                'text': '',
                'format': file_ext,
                'error': f'Unsupported format: {file_ext}'
            }
        
        text = ""
        
        try:
            if file_ext == '.pdf':
                text = self.extract_from_pdf(str(path))
            elif file_ext == '.docx':
                text = self.extract_from_docx(str(path))
            elif file_ext == '.doc':
                # .doc files require antiword or similar - skip for now
                logger.warning(f"DOC format not fully supported: {file_path}")
                text = ""
            elif file_ext == '.txt':
                text = self.extract_from_txt(str(path))
            
            return {
                'success': bool(text),
                'text': text,
                'format': file_ext,
                'error': None if text else 'No text extracted'
            }
        
        except Exception as e:
            logger.error(f"Text extraction error for {file_path}: {e}")
            return {
                'success': False,
                'text': '',
                'format': file_ext,
                'error': str(e)
            }


def extract_resume_text(file_path: str) -> str:
    """
    Convenience function to extract text from resume file
    
    Args:
        file_path: Path to resume file
        
    Returns:
        Extracted text or empty string
    """
    extractor = ResumeTextExtractor()
    result = extractor.extract_text(file_path)
    return result.get('text', '')


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python resume_text_extractor.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    result = extract_resume_text(file_path)
    
    if result:
        print(f"Extracted {len(result)} characters from {file_path}")
        print("\nFirst 500 characters:")
        print(result[:500])
    else:
        print(f"Failed to extract text from {file_path}")
