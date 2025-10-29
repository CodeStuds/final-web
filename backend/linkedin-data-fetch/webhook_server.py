#!/usr/bin/env python3
"""
Simple webhook server that receives LinkedIn scraped data and prints it to the terminal.
Also saves the data to text files in the output/ directory.
"""

from flask import Flask, request, jsonify
from datetime import datetime
import sys
import os
import re
from pathlib import Path
from bs4 import BeautifulSoup
import html2text

app = Flask(__name__)

# Create output directory if it doesn't exist
OUTPUT_DIR = Path('output')
OUTPUT_DIR.mkdir(exist_ok=True)

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_separator():
    """Print a separator line."""
    print(f"\n{Colors.OKBLUE}{'=' * 80}{Colors.ENDC}\n")


def extract_profile_name(url, title):
    """
    Extract a clean profile name from the URL or title for the filename.

    Args:
        url: LinkedIn URL
        title: Page title

    Returns:
        Clean filename (without extension)
    """
    # Try to extract from URL first (e.g., /in/john-doe -> john-doe)
    if '/in/' in url:
        match = re.search(r'/in/([^/?]+)', url)
        if match:
            return match.group(1)

    # Try to extract from company URL (e.g., /company/google -> company-google)
    if '/company/' in url:
        match = re.search(r'/company/([^/?]+)', url)
        if match:
            return f"company-{match.group(1)}"

    # Try to extract from job posting
    if '/jobs/view/' in url:
        match = re.search(r'/jobs/view/(\d+)', url)
        if match:
            return f"job-{match.group(1)}"

    # Fall back to cleaning the title
    if title and title != 'N/A':
        # Remove common LinkedIn suffixes
        clean_title = title.replace(' | LinkedIn', '').replace(' - LinkedIn', '')
        # Take first part before pipe or dash
        clean_title = re.split(r'[\|\-]', clean_title)[0].strip()
        # Clean up for filename (remove special chars, replace spaces with hyphens)
        clean_title = re.sub(r'[^\w\s-]', '', clean_title)
        clean_title = re.sub(r'[-\s]+', '-', clean_title)
        return clean_title.lower()[:50]  # Limit length

    # Last resort: use timestamp
    return f"linkedin-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def html_to_clean_text(html_content):
    """
    Convert HTML to clean, readable text using BeautifulSoup and html2text.

    Args:
        html_content: HTML string

    Returns:
        Clean text string
    """
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove remaining unwanted elements
    for element in soup.find_all(['script', 'style', 'svg', 'path']):
        element.decompose()

    # Configure html2text for cleaner output
    h = html2text.HTML2Text()
    h.ignore_links = True  # Remove URLs but keep link text
    h.ignore_images = True  # Remove images
    h.ignore_emphasis = False  # Keep bold/italic
    h.body_width = 0  # Don't wrap lines
    h.skip_internal_links = True
    h.inline_links = False
    h.protect_links = False
    h.mark_code = True

    # Convert to text
    text = h.handle(str(soup))

    # Clean up the text
    text = text.strip()

    # Remove excessive blank lines (more than 2)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove lines that are just special characters
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Keep line if it has actual text (not just punctuation/symbols)
        if stripped and not re.match(r'^[\W_]+$', stripped):
            cleaned_lines.append(line)
        elif not stripped:
            # Keep empty lines for spacing
            cleaned_lines.append('')

    text = '\n'.join(cleaned_lines)

    # Final cleanup: remove more than 2 consecutive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def save_to_file(profile_name, content, url, title, timestamp):
    """
    Save scraped content to a text file.

    Args:
        profile_name: Name for the file
        content: Text content to save
        url: Source URL
        title: Page title
        timestamp: When scraped

    Returns:
        Path to saved file
    """
    filename = f"{profile_name}.txt"
    filepath = OUTPUT_DIR / filename

    # Create header for the file
    header = f"""LinkedIn Profile Data
{'=' * 80}
Scraped: {timestamp}
URL: {url}
Title: {title}
{'=' * 80}

"""

    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(header)
        f.write(content)

    return filepath


@app.route('/webhook', methods=['POST'])
def webhook():
    """Receive webhook data, save to file, and print to terminal."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data received'}), 400

        # Extract data
        url = data.get('url', 'N/A')
        title = data.get('title', 'N/A')
        timestamp = data.get('timestamp', 'N/A')
        html_content = data.get('html', '')

        # Convert HTML to clean text
        clean_text = html_to_clean_text(html_content)

        # Extract profile name for filename
        profile_name = extract_profile_name(url, title)

        # Save to file
        filepath = save_to_file(profile_name, clean_text, url, title, timestamp)

        # Print formatted output
        print_separator()
        print(f"{Colors.BOLD}{Colors.HEADER}LinkedIn Data Received{Colors.ENDC}")
        print(f"{Colors.OKCYAN}Timestamp:{Colors.ENDC} {timestamp}")
        print(f"{Colors.OKCYAN}URL:{Colors.ENDC} {url}")
        print(f"{Colors.OKCYAN}Title:{Colors.ENDC} {title}")
        print(f"{Colors.OKGREEN}Saved to:{Colors.ENDC} {filepath}")
        print(f"\n{Colors.BOLD}{Colors.OKGREEN}Content Preview:{Colors.ENDC}\n")

        # Print first 500 characters as preview
        preview = clean_text[:500] + ('...' if len(clean_text) > 500 else '')
        print(preview)

        print(f"\n{Colors.WARNING}Full content saved to: {filepath}{Colors.ENDC}")
        print_separator()

        # Flush output to ensure it's displayed immediately
        sys.stdout.flush()

        return jsonify({
            'status': 'success',
            'message': f'Data saved to {filepath}',
            'filepath': str(filepath),
            'received_at': datetime.now().isoformat()
        }), 200

    except Exception as e:
        error_msg = f"Error processing webhook: {str(e)}"
        print(f"{Colors.FAIL}{error_msg}{Colors.ENDC}")
        return jsonify({'error': error_msg}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with info."""
    return jsonify({
        'name': 'LinkedIn Data Scraper Webhook',
        'version': '1.0.0',
        'endpoints': {
            '/webhook': 'POST - Receive scraped LinkedIn data',
            '/health': 'GET - Health check',
            '/': 'GET - This info page'
        }
    }), 200


if __name__ == '__main__':
    print(f"{Colors.BOLD}{Colors.OKGREEN}Starting LinkedIn Data Scraper Webhook Server{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Server running on: {Colors.ENDC}http://localhost:5000")
    print(f"{Colors.OKCYAN}Webhook endpoint: {Colors.ENDC}http://localhost:5000/webhook")
    print(f"{Colors.OKCYAN}Output directory: {Colors.ENDC}{OUTPUT_DIR.absolute()}")
    print(f"{Colors.WARNING}Waiting for data...{Colors.ENDC}\n")

    # Run with CORS enabled for browser extension
    from flask_cors import CORS
    CORS(app)

    app.run(host='0.0.0.0', port=5000, debug=True)
