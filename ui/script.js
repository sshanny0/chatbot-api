const input = document.querySelector(".textInput");
const sendBtn = document.querySelector(".send-button");
const messageList = document.querySelector(".message");
const chatButton = document.getElementById("chatButton");
const chatBox = document.getElementById("chatBox");
const closeChat = document.getElementById("closeChat"); 

document.querySelectorAll(".suggestions li").forEach((item) => {
  item.addEventListener("click", () => {
    sendMessage(item.innerText);
  });
});

chatButton.addEventListener("click", () => {
  chatBox.classList.toggle("hidden");
});

closeChat.addEventListener("click", () => {
  chatBox.classList.add("hidden");
});

function addMessage(text, sender = "me") {
  if (!text) return;

  const li = document.createElement("li");
  li.className = sender;

  const avatar =
    sender === "sender"
      ? `<img src="../img/icon-helpdesk.png" alt="icon-message">`
      : "";

  const content = document.createElement("div");
  content.className = "message-content";

  li.innerHTML = `
        ${avatar}
        <div class="message-content">
            <p>${text}</p>
        </div>
    `;

  messageList.appendChild(li);
  messageList.scrollTop = messageList.scrollHeight;
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

  require('dotenv').config();
  fetch(process.env.LOCAL_SITE + process.env.LOCAL_API, { // # local
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
        addMessage(data.Jawaban, "sender");
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
