// Popup script for the browser extension

const webhookUrlInput = document.getElementById('webhookUrl');
const scrapeButton = document.getElementById('scrapeButton');
const statusDiv = document.getElementById('status');

// Load saved webhook URL
chrome.storage.sync.get(['webhookUrl'], (result) => {
  if (result.webhookUrl) {
    webhookUrlInput.value = result.webhookUrl;
  } else {
    webhookUrlInput.value = 'http://localhost:5000/webhook';
  }
});

// Save webhook URL when it changes
webhookUrlInput.addEventListener('change', () => {
  chrome.storage.sync.set({ webhookUrl: webhookUrlInput.value });
});

// Show status message
function showStatus(message, type = 'info') {
  statusDiv.textContent = message;
  statusDiv.className = type;
  statusDiv.style.display = 'block';

  if (type === 'success' || type === 'error') {
    setTimeout(() => {
      statusDiv.style.display = 'none';
    }, 5000);
  }
}

// Scrape button click handler
scrapeButton.addEventListener('click', async () => {
  const webhookUrl = webhookUrlInput.value.trim();

  if (!webhookUrl) {
    showStatus('Please enter a webhook URL', 'error');
    return;
  }

  // Save the webhook URL
  chrome.storage.sync.set({ webhookUrl });

  // Check if we're on LinkedIn
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  if (!tab.url.includes('linkedin.com')) {
    showStatus('This extension only works on LinkedIn pages', 'error');
    return;
  }

  // Disable button and show status
  scrapeButton.disabled = true;
  showStatus('Scraping page...', 'info');

  try {
    // Send message to content script to scrape the page
    chrome.tabs.sendMessage(
      tab.id,
      { action: 'scrapeData' },
      (response) => {
        scrapeButton.disabled = false;

        if (chrome.runtime.lastError) {
          showStatus('Error: ' + chrome.runtime.lastError.message, 'error');
          console.error('Error:', chrome.runtime.lastError);
          return;
        }

        if (response && response.success) {
          showStatus('Data scraped and sent successfully!', 'success');
        } else {
          showStatus('Error: ' + (response?.error || 'Unknown error'), 'error');
        }
      }
    );
  } catch (error) {
    scrapeButton.disabled = false;
    showStatus('Error: ' + error.message, 'error');
    console.error('Error:', error);
  }
});
