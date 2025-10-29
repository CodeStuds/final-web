// Background service worker

console.log('LinkedIn Data Scraper: Background script loaded');

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'sendToWebhook') {
    console.log('LinkedIn Data Scraper: Received data to send to webhook');

    // Get the webhook URL from storage
    chrome.storage.sync.get(['webhookUrl'], async (result) => {
      const webhookUrl = result.webhookUrl || 'http://localhost:5000/webhook';

      try {
        console.log('LinkedIn Data Scraper: Sending to webhook:', webhookUrl);

        const response = await fetch(webhookUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(request.data),
        });

        if (response.ok) {
          const responseData = await response.text();
          console.log('LinkedIn Data Scraper: Webhook response:', responseData);
          sendResponse({ success: true, message: 'Data sent successfully' });
        } else {
          const errorText = await response.text();
          console.error('LinkedIn Data Scraper: Webhook error:', errorText);
          sendResponse({
            success: false,
            error: `Webhook returned status ${response.status}: ${errorText}`,
          });
        }
      } catch (error) {
        console.error('LinkedIn Data Scraper: Error sending to webhook:', error);
        sendResponse({
          success: false,
          error: error.message || 'Failed to send data to webhook',
        });
      }
    });

    // Return true to indicate we'll respond asynchronously
    return true;
  }
});
