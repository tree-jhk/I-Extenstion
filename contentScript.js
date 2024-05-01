function addListItem() {
  const ul = document.getElementsByClassName("left-menus")[0];
  if (ul) {
    const newLi = document.createElement("li");
    newLi.setAttribute("id", "i-quiz-link");
    newLi.setAttribute("data-original-title", "New Quiz Link");
    newLi.setAttribute("title", "New Quiz Link");

    newLi.addEventListener("mouseover", function () {
      this.style.backgroundColor = "#484B53";
    });
    newLi.addEventListener("mouseout", function () {
      this.style.backgroundColor = "#2F3033";
    });

    newLi.style.cssText = `
      cursor: pointer;
      height: 60px;
      background-color: #2F3033;
      text-overflow: ellipsis;
      border-bottom: 1px solid #252626;
    `;

    newLi.addEventListener("click", replaceMainDiv);

    const link = document.createElement("a");
    link.setAttribute("href", "https://learn.inha.ac.kr/#iquiz/quiz");
    link.setAttribute("class", "left-menu-link left-menu-link-message");
    link.setAttribute("title", "Message");
    link.setAttribute("data-toggle", "tooltip");
    link.setAttribute("data-placement", "right");

    const h5 = document.createElement("h5");
    h5.className = "nosubmenu";
    h5.textContent = "I-Quiz";
    link.appendChild(h5);

    newLi.appendChild(link);

    ul.appendChild(newLi);
  }
}

function replaceMainDiv() {
  const regionMain = document.getElementById("region-main");
  if (regionMain && regionMain.children.length > 1) {
    const secondChild = regionMain.children[1];
    const newDiv = document.createElement("div");
    newDiv.className = "chat-container";
    newDiv.innerHTML = `
    <div class="chat-interface">
    <div class="left-panel">
      <h3>Customize Your Chat persona:)</h3>
      <div class="option-group">
        <h4>Demographic Cues</h4>
        <label class="toggle-switch">
          <input type="checkbox">
          <span class="toggle-slider"></span>
        </label>
        <div class="verbal-style-group">
          <label><input type="radio" name="demographic" value="yuri"> Yuri</label>
          <label><input type="radio" name="demographic" value="no-gender"> No gender</label>
        </div>
      </div>
      <div class="option-group">
        <h4>Verbal Style Cues</h4>
        <label class="toggle-switch">
          <input type="checkbox">
          <span class="toggle-slider"></span>
        </label>
        <div class="verbal-style-group">
          <label><input type="radio" name="verbal-style" value="unpredictable"> Unpredictable</label>
          <label><input type="radio" name="verbal-style" value="curious"> Curious</label>
          <label><input type="radio" name="verbal-style" value="snarky"> Snarky</label>
          <label><input type="radio" name="verbal-style" value="unusual"> Unusual</label>
          <label><input type="radio" name="verbal-style" value="funny"> Funny</label>
          <label><input type="radio" name="verbal-style" value="non-judgmental"> Non-judgmental</label>
          <label><input type="radio" name="verbal-style" value="curious"> Curious</label>
          <label><input type="radio" name="verbal-style" value="caring"> Caring</label>
          <label><input type="radio" name="verbal-style" value="creative"> Creative</label>
          <label><input type="radio" name="verbal-style" value="casual"> Casual</label>
          <label><input type="radio" name="verbal-style" value="neurotic"> Neurotic</label>
          <label><input type="radio" name="verbal-style" value="rational"> Rational</label>
        </div>
      </div>
      <div class="option-group">
        <h4>Emoji</h4>
        <label class="toggle-switch">
          <input type="checkbox">
          <span class="toggle-slider"></span>
        </label>
      </div>
      <div class="option-group">
        <h4>Knowledge and Interest Cues</h4>
        <label class="toggle-switch">
          <input type="checkbox">
          <span class="toggle-slider"></span>
        </label>
        <div class="verbal-style-group">
          <label><input type="radio" name="knowledge" value="shamanism"> Shamanism</label>
          <label><input type="radio" name="knowledge" value="psychology"> Psychology</label>
          <label><input type="radio" name="knowledge" value="neuroscience-rights"> Neuroscience rights</label>
        </div>
      </div>
      <div class="option-group">
        <h4>Other settings</h4>
        <label class="toggle-switch">
          <input type="checkbox">
          <span class="toggle-slider"></span>
        </label>
        <div class="verbal-style-group">
          <label><input type="radio" name="other-settings" value="small-talk"> Small talk</label>
          <label><input type="radio" name="other-settings" value="meta-relational-talk"> Meta-relational talk</label>
          <label><input type="radio" name="other-settings" value="humor"> Humor</label>
          <label><input type="radio" name="other-settings" value="greeting"> Greeting</label>
        </div>
      </div>
      <div class="option-group">
        <h4>Appearance</h4>
        <!-- Add appearance options here -->
      </div>
    </div>
    <div class="right-panel">
      <div id="messages"></div>
      <div class="input-container">
        <input type="text" id="message-input" placeholder="Type your message...">
        <button id="sendButton">Send</button>
      </div>
    </div>
  </div>
    `;

    newDiv.style.cssText = `
      height: 500px;
      border: 1px solid #ccc;
      padding: 10px;
      overflow-y: scroll;
      background: #f9f9f9;
      font-family: Arial, sans-serif;
    `;

    regionMain.replaceChild(newDiv, secondChild);

    // Add event listener for send button
    const sendButton = document.getElementById("sendButton");
    sendButton.addEventListener("click", sendMessage);
  }
}

function sendMessage() {
  const input = document.getElementById("message-input");
  const message = input.value.trim();
  if (message) {
    const messagesContainer = document.getElementById("messages");
    const messageDiv = document.createElement("div");
    messageDiv.textContent = message;
    messagesContainer.appendChild(messageDiv);
    input.value = ""; // Clear the input field

    // Send the message to the background script for processing
    chrome.runtime.sendMessage({ type: "sendMessage", message: message }, (response) => {
      const responseDiv = document.createElement("div");
      responseDiv.textContent = response.answer;
      messagesContainer.appendChild(responseDiv);
      messagesContainer.scrollTop = messagesContainer.scrollHeight; // Scroll to the bottom
    });
  }
}

window.onload = addListItem;