# LinkedIn Data Scraper - Project Overview

## What This Does

This project consists of two main components:

1. **Browser Extension** - Runs in Chrome/Edge/Firefox and scrapes LinkedIn pages
2. **Python Webhook Server** - Receives the scraped data and displays it in the terminal

### Data Flow

```
User clicks "Scrape"
       ↓
Extension extracts HTML from LinkedIn page
       ↓
Turndown.js converts HTML → Markdown
       ↓
Extension sends data to webhook via POST request
       ↓
Python server receives data
       ↓
Server prints formatted Markdown to terminal
```

## Key Features

- **LinkedIn-only**: Only activates on linkedin.com domains
- **HTML to Markdown**: Clean conversion using Turndown.js library
- **Configurable webhook**: Set any webhook URL (defaults to localhost:5000)
- **Real-time output**: See scraped data immediately in terminal
- **Manifest V3**: Uses latest Chrome extension standard

## Technical Stack

### Browser Extension
- **Manifest V3** (latest Chrome extension format)
- **Vanilla JavaScript** (no frameworks needed)
- **Turndown.js** (HTML to Markdown conversion)
- **Chrome Extension APIs**: tabs, storage, runtime messaging

### Webhook Server
- **Python 3.7+**
- **Flask** (lightweight web framework)
- **Flask-CORS** (cross-origin support)
- **ANSI colors** (terminal formatting)

## File Structure

```
linkedin-data-fetch/
│
├── Browser Extension Files
│   ├── manifest.json          # Extension configuration (Manifest V3)
│   ├── popup.html            # Extension popup interface
│   ├── popup.js              # Popup logic and UI handling
│   ├── content.js            # Runs on LinkedIn pages, does scraping
│   ├── background.js         # Service worker for webhook communication
│   ├── turndown.min.js       # HTML → Markdown conversion library
│   ├── icon16.png            # Extension icon (16x16)
│   ├── icon48.png            # Extension icon (48x48)
│   └── icon128.png           # Extension icon (128x128)
│
├── Python Webhook Server
│   ├── webhook_server.py     # Flask server that receives data
│   └── requirements.txt      # Python dependencies
│
├── Setup & Utilities
│   ├── generate_icons.py     # Python script to create icons
│   ├── create_icons.sh       # Shell script for icon creation
│   ├── test_setup.sh         # Verify installation
│   └── icon.svg              # SVG source for icons
│
└── Documentation
    ├── README.md             # Full documentation
    ├── QUICKSTART.md         # Quick start guide
    └── PROJECT_OVERVIEW.md   # This file
```

## Component Details

### 1. Content Script (content.js)

**Runs on**: All LinkedIn pages
**Purpose**: Listens for scrape commands and extracts page content
**Key functions**:
- Finds the main content area (`<main>` tag or `<body>`)
- Uses Turndown to convert HTML to Markdown
- Collects metadata (URL, title, timestamp)
- Sends data to background script

### 2. Background Script (background.js)

**Runs as**: Service worker (Manifest V3)
**Purpose**: Handles webhook communication
**Key functions**:
- Receives data from content script
- Gets webhook URL from storage
- Sends POST request to webhook
- Returns success/failure to content script

### 3. Popup UI (popup.html + popup.js)

**Triggered by**: Clicking extension icon
**Purpose**: User interface for the extension
**Features**:
- Webhook URL configuration
- "Scrape This Page" button
- Status messages (success/error/info)
- Saves settings to Chrome storage

### 4. Webhook Server (webhook_server.py)

**Runs on**: localhost:5000 (configurable)
**Purpose**: Receives and displays scraped data
**Endpoints**:
- `POST /webhook` - Receives scraped data
- `GET /health` - Health check
- `GET /` - Info page

**Features**:
- CORS support for browser extension
- Colored terminal output
- JSON request/response
- Error handling

## Data Format

### Request to Webhook

```json
{
  "url": "https://www.linkedin.com/in/username",
  "title": "John Doe - Job Title - Company | LinkedIn",
  "timestamp": "2025-10-29T13:12:00.000Z",
  "markdown": "# Heading\n\nContent in markdown format..."
}
```

### Response from Webhook

```json
{
  "status": "success",
  "message": "Data received and printed to terminal",
  "received_at": "2025-10-29T13:12:00.123456"
}
```

## Security Considerations

### What's Safe
- Extension only runs on linkedin.com domains
- Data only sent to webhook you configure
- Default webhook is localhost (your machine only)
- No data is stored permanently

### What to Be Aware Of
- Scraped data may contain personal information
- Webhook sends data over HTTP (unencrypted) by default
- For production, use HTTPS and add authentication

## Customization Ideas

### Extension Side
1. **Selective scraping**: Modify `content.js` to scrape specific sections
2. **Multiple formats**: Add JSON, CSV export options
3. **Auto-scrape**: Automatically scrape pages as you browse
4. **Batch mode**: Scrape multiple pages at once
5. **Save locally**: Store data in browser storage or download files

### Server Side
1. **Database storage**: Save scraped data to SQLite/PostgreSQL
2. **File export**: Write each scrape to a separate .md file
3. **API integration**: Forward data to other services
4. **Search**: Build a search index of scraped content
5. **Authentication**: Add API keys or OAuth

## Performance Notes

- **Memory**: Turndown.js processes HTML in-memory (fine for most pages)
- **Network**: Each scrape = 1 POST request to webhook
- **Storage**: Extension settings use Chrome sync storage (limited to 100KB)
- **Speed**: Scraping is near-instant for typical LinkedIn pages

## Browser Compatibility

### Fully Supported
- Chrome 88+ ✓
- Edge 88+ ✓
- Opera 74+ ✓

### Partial Support
- Firefox (requires Manifest V2 conversion)
- Safari (requires Manifest V2 conversion)

Note: This extension uses Manifest V3, which is the current standard for Chromium browsers.

## Common Use Cases

1. **Profile scraping**: Save LinkedIn profiles for research
2. **Job listings**: Convert job postings to readable format
3. **Company research**: Extract company page information
4. **Content archival**: Save posts and articles
5. **Data analysis**: Collect structured data for analysis

## Limitations

- Requires manual click to scrape (no auto-scraping)
- LinkedIn's dynamic content may not fully render
- Some elements (images, videos) convert to markdown links only
- Rate limiting: LinkedIn may block excessive requests
- Login required: Extension can't scrape pages you can't access

## Troubleshooting Tips

### Extension Issues
- Check browser console (F12 → Console) for errors
- Verify you're on a linkedin.com page
- Reload the extension after code changes
- Check manifest.json for syntax errors

### Server Issues
- Ensure Flask dependencies are installed
- Check port 5000 isn't already in use
- Verify CORS is enabled (flask-cors installed)
- Look at server logs for error messages

### Connection Issues
- Confirm webhook URL matches server address
- Check firewall isn't blocking port 5000
- Try curl to test webhook: `curl -X POST http://localhost:5000/webhook`

## Development Workflow

1. Make changes to extension files
2. Go to `chrome://extensions/`
3. Click reload button on your extension
4. Navigate to LinkedIn page
5. Test the changes
6. Check browser console and terminal for logs

## Resources

- [Chrome Extension Docs](https://developer.chrome.com/docs/extensions/)
- [Turndown.js Docs](https://github.com/mixmark-io/turndown)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Manifest V3 Migration](https://developer.chrome.com/docs/extensions/mv3/intro/)

## Contributing

Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Share improvements

## License

MIT License - use freely for personal or commercial projects!

---

**Need Help?**
- Read [QUICKSTART.md](QUICKSTART.md) for setup
- Check [README.md](README.md) for detailed docs
- Run `./test_setup.sh` to verify installation
