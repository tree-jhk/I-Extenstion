function addListItem() {
  // getElementsByClassName은 NodeList를 반환하므로 첫 번째 요소를 선택합니다.
  const ul = document.getElementsByClassName("left-menus")[0];
  console.log(ul);
  if (ul) {
    const newLi = document.createElement("li");
    newLi.setAttribute("id", "i-quiz-link");
    newLi.setAttribute("data-original-title", "New Quiz Link");
    newLi.setAttribute("title", "New Quiz Link");

    // 마우스를 올렸을 때의 스타일
    newLi.addEventListener("mouseover", function () {
      this.style.backgroundColor = "#484B53";
    });
    // 마우스가 떠났을 때 원래 스타일로 복귀
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

    // 새로운 a 태그 생성
    const link = document.createElement("a");
    link.setAttribute("href", "https://learn.inha.ac.kr/#iquiz/quiz");
    link.setAttribute("class", "left-menu-link left-menu-link-message");
    link.setAttribute("title", "Message");
    link.setAttribute("data-toggle", "tooltip");
    link.setAttribute("data-placement", "right");

    // h5 태그와 텍스트 추가
    const h5 = document.createElement("h5");
    h5.className = "nosubmenu";
    h5.textContent = "I-Quiz";
    link.appendChild(h5);

    // newLi에 링크 추가
    newLi.appendChild(link);

    // ul 요소에 newLi 추가
    ul.appendChild(newLi);
  }
}

function replaceMainDiv() {
  const regionMain = document.getElementById("region-main");
  if (regionMain && regionMain.children.length > 1) {
    const secondChild = regionMain.children[1]; // 두 번째 자식 요소 선택
    const newDiv = document.createElement("div");
    newDiv.className = "chat-container";
    newDiv.innerHTML = `
      <div id="messages" style="height: 90%; overflow-y: auto; margin-bottom: 10px; padding: 5px; background: #fff; border: 1px solid #ddd;"></div>
      <input type="text" id="message-input" style="width: calc(100% - 90px); margin-top: 10px; padding: 8px; border: 1px solid #ddd;">
      <button id="sendButton">Send</button>
    `;

    // 스타일 설정
    newDiv.style.cssText = `
      height: 500px;
      border: 1px solid #ccc;
      padding: 10px;
      overflow-y: scroll;
      background: #f9f9f9;
      font-family: Arial, sans-serif;
    `;

    regionMain.replaceChild(newDiv, secondChild);

    // 메시지 보내기 함수 추가
    const sendButton = document.getElementById("sendButton");
    sendButton.addEventListener("click", function () {
      const input = document.getElementById("message-input");
      const message = input.value.trim();
      if (message) {
        const messagesContainer = document.getElementById("messages");
        const messageDiv = document.createElement("div");
        messageDiv.textContent = message;
        messagesContainer.appendChild(messageDiv);
        input.value = ""; // 입력 필드 초기화
        messagesContainer.scrollTop = messagesContainer.scrollHeight; // 스크롤을 최하단으로 이동
      }
    });
  }
}

window.onload = addListItem;
