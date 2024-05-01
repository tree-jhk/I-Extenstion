chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "sendMessage") {
    const message = request.message;
    // Process the message and generate a response using GPT-3.5 API
    const answer = "This is a sample response from GPT-3.5 API.";
    sendResponse({ answer: answer });
  }
});