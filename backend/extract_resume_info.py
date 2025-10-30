#!/usr/bin/env python3
"""
Resume Information Extractor

Extracts candidate information (name, GitHub, LinkedIn, LeetCode links)
from .txt resume files in a ZIP archive and outputs to CSV.
"""

import zipfile
import re
import csv
import os
from pathlib import Path


def extract_urls(text, pattern):
    """Extract URLs matching a specific pattern from text."""
    matches = re.findall(pattern, text, re.IGNORECASE)
    return matches[0] if matches else ""


def extract_candidate_name(text, filename):
    """
    Attempt to extract candidate name from resume text.
    Uses multiple strategies to find the most likely candidate name.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    if not lines:
        return ""

    # Strategy 1: Look for common name patterns in first few lines
    # Names are often at the top, before contact info
    for i, line in enumerate(lines[:5]):
        # Skip lines that look like contact info or headers
        if any(keyword in line.lower() for keyword in
               ['email', '@', 'phone', 'address', 'resume', 'cv', 'http', 'linkedin', 'github']):
            continue

        # Check if line looks like a name (2-4 words, capitalized, no special chars)
        words = line.split()
        if 2 <= len(words) <= 4:
            if all(word[0].isupper() if word else False for word in words):
                if not any(char.isdigit() for char in line):
                    return line

    # Strategy 2: Look for "Name:" or similar labels
    name_pattern = r'(?:Name|Candidate|Full Name)[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
    match = re.search(name_pattern, text, re.IGNORECASE)
    if match:
        return match.group(1)

    # Strategy 3: Use filename if it looks like a name
    filename_base = Path(filename).stem
    # Remove common suffixes like _resume, -CV, etc.
    filename_clean = re.sub(r'[-_](resume|cv|profile).*', '', filename_base, flags=re.IGNORECASE)
    filename_clean = filename_clean.replace('_', ' ').replace('-', ' ').strip()

    words = filename_clean.split()
    if 2 <= len(words) <= 4 and all(word[0].isupper() if word else False for word in words):
        return filename_clean

    # Strategy 4: Return first non-empty line if nothing else works
    return lines[0][:50] if lines else ""


def extract_resume_info(zip_path, output_csv='resume_info.csv'):
    """
    Extract candidate information from resumes in a ZIP file.

    Args:
        zip_path: Path to the resumes.zip file
        output_csv: Path for the output CSV file
    """
    results = []

    # URL patterns
    github_pattern = r'https?://(?:www\.)?github\.com/[\w\-]+'
    linkedin_pattern = r'https?://(?:www\.)?linkedin\.com/in/[\w\-]+'
    leetcode_pattern = r'https?://(?:www\.)?leetcode\.com/[\w\-]+'

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get list of .txt files
            txt_files = [f for f in zip_ref.namelist()
                        if f.endswith('.txt') and not f.startswith('__MACOSX')]

            print(f"Found {len(txt_files)} resume files in ZIP archive")

            for filename in txt_files:
                print(f"Processing: {filename}")

                # Read file content
                with zip_ref.open(filename) as file:
                    try:
                        content = file.read().decode('utf-8')
                    except UnicodeDecodeError:
                        # Try with different encoding if UTF-8 fails
                        content = file.read().decode('latin-1')

                # Extract information
                candidate_name = extract_candidate_name(content, filename)
                github_link = extract_urls(content, github_pattern)
                linkedin_link = extract_urls(content, linkedin_pattern)
                leetcode_link = extract_urls(content, leetcode_pattern)

                results.append({
                    'File_Name': os.path.basename(filename),
                    'Candidate_Name': candidate_name,
                    'GitHub_Link': github_link,
                    'LinkedIn_Link': linkedin_link,
                    'LeetCode_Link': leetcode_link
                })

    except FileNotFoundError:
        print(f"Error: ZIP file '{zip_path}' not found")
        return
    except zipfile.BadZipFile:
        print(f"Error: '{zip_path}' is not a valid ZIP file")
        return

    # Write results to CSV
    if results:
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['File_Name', 'Candidate_Name', 'GitHub_Link',
                         'LinkedIn_Link', 'LeetCode_Link']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(results)

        print(f"\n✓ Successfully processed {len(results)} resumes")
        print(f"✓ Results saved to: {output_csv}")

        # Print summary
        print("\nSummary:")
        print(f"  - Resumes with GitHub links: {sum(1 for r in results if r['GitHub_Link'])}")
        print(f"  - Resumes with LinkedIn links: {sum(1 for r in results if r['LinkedIn_Link'])}")
        print(f"  - Resumes with LeetCode links: {sum(1 for r in results if r['LeetCode_Link'])}")
    else:
        print("No resume files found or processed")


if __name__ == "__main__":
    # Process resumes.zip and create resume_info.csv
    extract_resume_info('resumes.zip', 'resume_info.csv')
