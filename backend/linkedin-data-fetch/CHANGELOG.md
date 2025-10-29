# Changelog

## [2.0.0] - 2025-10-29 - Major Improvement

### Fixed
- **Critical:** Previous implementation removed 80% of content due to overly aggressive filtering
- Text extraction now preserves all important content while still removing clutter

### Changed
- **content.js**: Switched from client-side Turndown processing to sending clean HTML
- **webhook_server.py**: Implemented BeautifulSoup4 + html2text for better text extraction
- Data sent as HTML instead of pre-processed markdown for better server-side control

### Added
- New dependencies: `beautifulsoup4`, `html2text`
- New function: `html_to_clean_text()` for intelligent HTML parsing
- IMPROVEMENTS.md with detailed technical explanation
- CHANGELOG.md (this file)

### Technical Details
- html2text configured with `ignore_links=True` to remove URLs but keep link text
- BeautifulSoup removes remaining unwanted elements before conversion
- Smart post-processing removes special-character-only lines
- Whitespace normalization (max 2 consecutive newlines)

### Migration
1. Update dependencies: `pip install -r requirements.txt`
2. Reload browser extension
3. Restart webhook server

---

## [1.0.0] - 2025-10-29 - Initial Release

### Added
- Browser extension for LinkedIn scraping
- Manifest V3 support
- Turndown.js for HTML to Markdown conversion
- Python Flask webhook server
- Automatic file saving to output/<profile>.txt
- Smart filename extraction from URLs
- Terminal preview of scraped content

### Features
- Works only on LinkedIn.com domains
- Configurable webhook URL
- Removes ads, navigation, and UI clutter
- Colored terminal output
- CORS support for browser extension
