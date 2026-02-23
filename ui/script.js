const input = document.querySelector(".textInput");
const sendBtn = document.querySelector(".send-button");
const messageList = document.querySelector(".message");
const chatButton = document.getElementById("chatButton");
const chatBox = document.getElementById("chatBox");
const closeChat = document.getElementById("closeChat");
const chatBody = document.querySelector(".chat-body");
const nearBottom =
  chatBody.scrollHeight - chatBody.scrollTop <= chatBody.clientHeight + 50;
const scrollBtn = document.getElementById("scrollToBottomBtn");

chatButton.addEventListener("click", () => {
  chatBox.classList.toggle("hidden");
});

closeChat.addEventListener("click", () => {
  chatBox.classList.add("hidden");
});

function addMessage(text, sender = "me", link = null, tag = null) {
  if (!text) return;

  const li = document.createElement("li");
  li.className = sender;

  const avatar =
    sender === "sender"
      ? `<img src="../img/icon-helpdesk.png" alt="icon-message">`
      : "";

  li.innerHTML = `
    ${avatar}
    <div class="message-content">
      <p>
      ${text}
      ${link ? `<a href="${link}" target="_blank">${tag}</a>` : ""}
      </p>
    </div>
  `;

  messageList.appendChild(li);

    //SCROLL TO BOTTOM
  if (nearBottom) {
  chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });
  }
}

sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

function sendMessage(textFromSuggestion = null) {
  const text = textFromSuggestion || input.value.trim();
  if (!text) return;

  addMessage(text, "me");
  input.value = "";

  fetch("http://127.0.0.1:8000/chatbot/ask", {
    // fetch(process.env.URL_SITE + process.env.URL_API, { # dev
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question: text }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.Jawaban) {
        addMessage(
          data.Jawaban,
          "sender",
          data.Link?.url,
          data.Link?.tag
        );
      } else {
        addMessage(
          "Mohon maaf saya belum yakin dengan jawaban saya 🙏 Silakan hubungi Helpdesk TI ",
          "sender",
        );
      }
    })
    .catch(() => {
       addMessage("Server error ❎", "sender");
    });
}

// grouping by category for quick replies
function loadCategory(keyword) {

  fetch(`http://127.0.0.1:8000/chatbot/category/${encodeURIComponent(keyword)}`)
    .then(res => res.json())
    .then(data => {

      if (data.Status === "category") {
          renderCards(data.Data);
      }

    });

}

function renderCards(data) {

  const container = document.querySelector(".quick-replies");
  container.innerHTML = "";

  let cardsHTML = `
    <div class="card-slider">
      <div class="card-wrapper">
  `;

  data.forEach(item => {

    const hasLink = item.link && item.link.url && item.link.tag;

    cardsHTML += `
      <div class="bot-card">
        <strong>${item.question}</strong>
        <p>
          ${item.answer}
          ${
            hasLink
              ? `<a href="${item.link.url}" target="_blank">${item.link.tag}</a>`
              : ""
          }
        </p>
      </div>
    `;
  });

  cardsHTML += `
      </div>

      <div class="card-nav">
        <button class="prev">‹</button>
        <button class="next">›</button>
      </div>
    </div>
  `;

  container.innerHTML = cardsHTML;

  initSlider();
}


function initSlider() {

  const slider = document.querySelector(".card-slider");
  const wrapper = slider.querySelector(".card-wrapper");
  const cards = slider.querySelectorAll(".bot-card");

  let index = 0;

  function update() {
    wrapper.style.transform = `translateX(-${index * 100}%)`;
  }

  slider.querySelector(".next").onclick = () => {
    if (index < cards.length - 1) {
      index++;
      update();
    }
  };

  slider.querySelector(".prev").onclick = () => {
    if (index > 0) {
      index--;
      update();
    }
  };
}