// Content script that runs on LinkedIn pages
console.log('LinkedIn Data Scraper: Content script loaded');

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'scrapeData') {
    console.log('LinkedIn Data Scraper: Starting scrape...');

    try {
      // Get the main content area of LinkedIn
      const mainContent = document.querySelector('main') || document.body;

      if (!mainContent) {
        sendResponse({ success: false, error: 'Could not find main content' });
        return;
      }

      // Clone the content to avoid modifying the actual page
      const contentClone = mainContent.cloneNode(true);

      // Remove unwanted elements before sending to server
      const selectorsToRemove = [
        'script', 'style', 'noscript', 'svg', 'iframe',
        'nav', 'header', 'footer',
        '.artdeco-button', // LinkedIn buttons
        '.feed-shared-update-v2__social-actions', // Like/comment buttons
        '.scaffold-layout__sidebar', // Sidebar ads
        '.ad-banner-container', // Ad banners
        '[data-test-id*="ad"]', // Ad elements
        '.msg-overlay-list-bubble', // Message overlays
        '.global-nav', // Top navigation
        '.application-outlet' // App shell
      ];

      selectorsToRemove.forEach(selector => {
        contentClone.querySelectorAll(selector).forEach(el => el.remove());
      });

      // Get the cleaned HTML
      const cleanHtml = contentClone.innerHTML;

      // Get page metadata
      const pageData = {
        url: window.location.href,
        title: document.title,
        timestamp: new Date().toISOString(),
        html: cleanHtml
      };

      console.log('LinkedIn Data Scraper: Scrape complete, sending to background script');

      // Send to background script which will forward to webhook
      chrome.runtime.sendMessage(
        { action: 'sendToWebhook', data: pageData },
        (response) => {
          if (chrome.runtime.lastError) {
            console.error('Error sending to background:', chrome.runtime.lastError);
            sendResponse({ success: false, error: chrome.runtime.lastError.message });
          } else {
            sendResponse(response);
          }
        }
      );

      // Return true to indicate we'll respond asynchronously
      return true;

    } catch (error) {
      console.error('LinkedIn Data Scraper: Error during scrape:', error);
      sendResponse({ success: false, error: error.message });
    }
  }

  return true; // Keep the message channel open for async response
});
