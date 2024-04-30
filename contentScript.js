function addListItem() {
  const ul = document.getElementsByClassName("left-menus")[0];
  console.log(ul);
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
    newDiv.className = "webview-container";
    newDiv.innerHTML = `
      <iframe src="http://127.0.0.1:8080/" style="width: 100%; height: 100%; border: none;"></iframe>
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
  }
}

window.onload = addListItem;