# LinkedIn Data Scraper

A browser extension that scrapes structured data from LinkedIn pages, converts it to Markdown, and sends it to a webhook server.

## Features

- Scrapes content from any LinkedIn page
- Converts HTML to **clean text-only format** (no URLs, images, or clutter)
- Automatically removes navigation, ads, and unnecessary elements
- Sends data to a configurable webhook endpoint
- **Saves scraped data to `output/<profile>.txt` files**
- Python webhook server displays preview in terminal
- Only activates on LinkedIn.com domains

## Project Structure

```
linkedin-data-fetch/
├── manifest.json          # Extension manifest (Manifest V3)
├── popup.html            # Extension popup UI
├── popup.js              # Popup logic
├── content.js            # Content script that runs on LinkedIn pages
├── background.js         # Background service worker for webhook communication
├── turndown.min.js       # HTML to Markdown conversion library
├── webhook_server.py     # Python webhook server
├── requirements.txt      # Python dependencies
├── output/               # Directory where scraped data is saved
└── README.md            # This file
```

## Installation

### 1. Set Up the Browser Extension

#### Chrome/Edge:
1. Open your browser and navigate to `chrome://extensions/` (or `edge://extensions/`)
2. Enable "Developer mode" (toggle in the top right)
3. Click "Load unpacked"
4. Select the `linkedin-data-fetch` directory
5. The extension should now appear in your extensions list

#### Firefox:
1. Navigate to `about:debugging#/runtime/this-firefox`
2. Click "Load Temporary Add-on"
3. Select the `manifest.json` file from the `linkedin-data-fetch` directory

**Note:** You'll need to create icon files (icon16.png, icon48.png, icon128.png) for the extension. See `.icon-placeholder` for instructions, or the extension will work without icons but may show warnings.

### 2. Set Up the Python Webhook Server

1. Make sure you have Python 3.7+ installed:
   ```bash
   python3 --version
   ```

2. Install the required dependencies:
   ```bash
   cd linkedin-data-fetch
   pip install -r requirements.txt
   ```

3. Make the webhook server executable (optional):
   ```bash
   chmod +x webhook_server.py
   ```

## Usage

### 1. Start the Webhook Server

Run the Python webhook server in your terminal:

```bash
python3 webhook_server.py
```

You should see:
```
Starting LinkedIn Data Scraper Webhook Server
Server running on: http://localhost:5000
Webhook endpoint: http://localhost:5000/webhook
Output directory: /path/to/linkedin-data-fetch/output
Waiting for data...
```

The server will stay running and wait for incoming data. All scraped profiles will be saved to the `output/` directory.

### 2. Use the Browser Extension

1. Navigate to any LinkedIn page (profile, job posting, company page, feed, etc.)
2. Click the extension icon in your browser toolbar
3. Verify the webhook URL is set to `http://localhost:5000/webhook` (this is the default)
4. Click the "Scrape This Page" button
5. The extension will:
   - Extract the main content from the page
   - Remove URLs, images, navigation, and other clutter
   - Convert it to clean text format
   - Send it to the webhook server
6. Check your terminal for a preview and the `output/` folder for the saved file!

### Example Output

When you scrape a LinkedIn profile at `/in/john-doe`, the server will:
- Display a preview in the terminal
- Save the full content to `output/john-doe.txt`

The saved file will contain:
```
LinkedIn Profile Data
================================================================================
Scraped: 2025-10-29T13:12:00.000Z
URL: https://www.linkedin.com/in/john-doe
Title: John Doe - Software Engineer | LinkedIn
================================================================================

# John Doe
Software Engineer at Company

## About
Experienced software engineer...
```

## How It Works

### Browser Extension Flow

1. **Content Script** (`content.js`): Runs on all LinkedIn pages and listens for scrape commands
2. **Popup UI** (`popup.html` + `popup.js`): Provides the user interface for triggering scrapes and configuring the webhook URL
3. **Background Script** (`background.js`): Handles communication with the webhook server
4. **Turndown Library** (`turndown.min.js`): Converts HTML to Markdown

### Data Flow

```
LinkedIn Page → Content Script → Extract HTML → Convert to Markdown
                                                       ↓
Terminal Output ← Python Server ← Background Script ← Send Data
```

### Webhook Server

The Python Flask server:
- Listens on `http://localhost:5000`
- Receives POST requests at `/webhook` endpoint
- Extracts clean profile names from URLs (e.g., `/in/john-doe` → `john-doe.txt`)
- Saves complete data to `output/<profile>.txt` files
- Displays a preview (first 500 characters) in the terminal
- Includes CORS support for browser extension communication

### File Naming

The server automatically generates filenames based on the LinkedIn URL:
- Profile: `/in/john-doe` → `output/john-doe.txt`
- Company: `/company/google` → `output/company-google.txt`
- Job: `/jobs/view/123456` → `output/job-123456.txt`
- Other pages: Uses cleaned page title or timestamp

## Configuration

### Change Webhook URL

1. Click the extension icon
2. Update the "Webhook URL" field
3. The new URL will be saved automatically

### Change Server Port

Edit `webhook_server.py` and change the port in the last line:

```python
app.run(host='0.0.0.0', port=5000, debug=True)  # Change 5000 to your desired port
```

Don't forget to update the webhook URL in the extension popup!

## API Reference

### Webhook Endpoint

**POST** `/webhook`

Receives scraped LinkedIn data.

**Request Body:**
```json
{
  "url": "https://www.linkedin.com/...",
  "title": "Page Title",
  "timestamp": "2025-10-29T12:00:00.000Z",
  "html": "<div>HTML content from LinkedIn page...</div>"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Data saved to output/john-doe.txt",
  "filepath": "output/john-doe.txt",
  "received_at": "2025-10-29T12:00:00.000000"
}
```

### Health Check

**GET** `/health`

Returns server health status.

## Troubleshooting

### Extension not working

- Make sure you're on a LinkedIn page (*.linkedin.com)
- Check the browser console for errors (F12 → Console)
- Try reloading the extension in the extensions page

### Webhook server not receiving data

- Verify the server is running (`python3 webhook_server.py`)
- Check the webhook URL in the extension popup matches the server URL
- Ensure no firewall is blocking port 5000
- Check the browser console and extension logs for errors

### CORS errors

- The webhook server includes CORS support via `flask-cors`
- If you still see CORS errors, verify `flask-cors` is installed:
  ```bash
  pip install flask-cors
  ```

### Missing dependencies

If you get import errors, install dependencies:
```bash
pip install -r requirements.txt
```

## Development

### Modify scraping behavior

Edit `content.js` to change what content is scraped. The current implementation:
- Scrapes the `<main>` element or falls back to `<body>`
- Removes links, images, navigation, scripts, and styles
- Cleans up excessive whitespace and formatting

To keep URLs in the output, remove or modify the `removeLinks` rule in content.js:663.

### Customize text cleaning

The extension performs aggressive cleaning to extract only text content. You can adjust this in `content.js`:
- Modify Turndown rules to keep/remove specific elements
- Adjust the post-processing regex patterns
- Change how whitespace is handled

### Add custom webhook processing

Edit `webhook_server.py` to add your own processing:
- Change how filenames are generated (see `extract_profile_name` function)
- Modify the file header format (see `save_to_file` function)
- Add database storage, API forwarding, or other integrations
- Change the preview length (default: 500 characters)

## Security Notes

- This extension only runs on LinkedIn.com domains
- Data is sent only to the webhook URL you configure
- The webhook server runs locally by default (localhost:5000)
- For production use, consider adding authentication to the webhook server

## License

MIT License - Feel free to modify and use as needed!

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## Future Enhancements

- Add support for scraping specific sections (e.g., only profile info)
- Batch scraping multiple pages
- Export to different formats (JSON, CSV, database)
- Add authentication to webhook server
- Browser sync for webhook URL across devices
- Automatic deduplication of profiles
- Search and filter saved profiles
