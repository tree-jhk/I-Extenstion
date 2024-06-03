// background.js

// Function to log a message when the extension is installed
chrome.runtime.onInstalled.addListener(function() {
    console.log("Blue Button Extension installed.");
});

// Function to log a message when the extension is started
chrome.runtime.onStartup.addListener(function() {
    console.log("Blue Button Extension started.");
});

// Function to log a message when the extension is updated
chrome.runtime.onUpdateAvailable.addListener(function() {
    console.log("Blue Button Extension update available.");
});

// Function to handle messages from content scripts
chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
    console.log("Message received from content script:", message);
    // Perform actions based on the message
    // For example, send a response back to the content script
    sendResponse({ received: true });
});
