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

  fetch("http://127.0.0.1:8000/ask", {
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
