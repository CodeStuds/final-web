# Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Create Extension Icons (One-time setup)

Before loading the extension, you need icon files. Choose one option:

### Option A: Quick placeholder icons
Download any small PNG image and copy it as all three icon sizes:
```bash
# If you have any PNG file, copy it:
cp your-image.png icon16.png
cp your-image.png icon48.png
cp your-image.png icon128.png
```

### Option B: Create proper icons with ImageMagick
```bash
sudo apt-get install imagemagick  # Ubuntu/Debian
# or: brew install imagemagick    # macOS

convert icon.svg -resize 16x16 icon16.png
convert icon.svg -resize 48x48 icon48.png
convert icon.svg -resize 128x128 icon128.png
```

### Option C: Use online tool
1. Visit https://www.favicon-generator.org/
2. Upload any image
3. Download the generated icons
4. Rename them to icon16.png, icon48.png, icon128.png

## Step 2: Install the Browser Extension

### Chrome/Edge:
1. Open `chrome://extensions/` (or `edge://extensions/`)
2. Enable "Developer mode" (toggle in top right corner)
3. Click "Load unpacked"
4. Select this folder: `linkedin-data-fetch`
5. Extension is now installed!

### Firefox:
1. Open `about:debugging#/runtime/this-firefox`
2. Click "Load Temporary Add-on"
3. Select the `manifest.json` file from this folder

## Step 3: Start the Webhook Server

```bash
# Install dependencies (first time only)
pip install -r requirements.txt

# Start the server
python3 webhook_server.py
```

You should see:
```
Starting LinkedIn Data Scraper Webhook Server
Server running on: http://localhost:5000
Webhook endpoint: http://localhost:5000/webhook
Waiting for data...
```

Keep this terminal window open!

## Step 4: Scrape LinkedIn Data

1. Open your browser and go to any LinkedIn page:
   - A profile: https://www.linkedin.com/in/someone
   - A job: https://www.linkedin.com/jobs/view/...
   - A company: https://www.linkedin.com/company/...
   - Your feed: https://www.linkedin.com/feed/

2. Click the extension icon in your browser toolbar

3. Verify webhook URL is `http://localhost:5000/webhook`

4. Click "Scrape This Page"

5. Check your terminal for a preview and the `output/` folder for the saved file!

## Example Output

When you scrape a profile at `/in/john-doe`, the server will:

1. **Save to file**: `output/john-doe.txt` with complete data
2. **Show preview in terminal**:

```
================================================================================

LinkedIn Data Received
Timestamp: 2025-10-29T12:34:56.789Z
URL: https://www.linkedin.com/in/john-doe
Title: John Doe - Software Engineer | LinkedIn
Saved to: output/john-doe.txt

Content Preview:

# John Doe
Software Engineer at Company

## About
Experienced software engineer specializing in...

[First 500 characters shown]

Full content saved to: output/john-doe.txt
================================================================================
```

The saved `.txt` file contains clean text-only content (no URLs, images, or clutter).

## Troubleshooting

### "Extension not loading" error
- Make sure you created the icon files (see Step 1)
- Check that you're in the correct directory

### "This extension only works on LinkedIn pages"
- Navigate to linkedin.com first
- Make sure the URL contains "linkedin.com"

### Webhook not receiving data
- Verify the Python server is running
- Check the webhook URL in the extension popup
- Look for errors in the browser console (F12 → Console)

### Port 5000 already in use
Edit `webhook_server.py` line 104:
```python
app.run(host='0.0.0.0', port=5001, debug=True)  # Changed to 5001
```
Then update the extension webhook URL to: `http://localhost:5001/webhook`

## What's Next?

- Read the full [README.md](README.md) for detailed documentation
- Customize the scraping behavior in `content.js`
- Modify the webhook processing in `webhook_server.py`
- Try scraping different LinkedIn pages (profiles, jobs, companies, posts)

## Tips

- The extension saves your webhook URL, so you only need to set it once
- You can scrape as many pages as you want while the server is running
- All scraped data is saved to the `output/` folder
- Files are named automatically based on the profile/company URL
- The output is clean text-only (no URLs, images, or navigation)
- Press Ctrl+C in the terminal to stop the webhook server
- Check the `output/` folder to see all your scraped profiles

Enjoy scraping!
