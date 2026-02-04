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

function linkify(text) {
  if (!text) return "";

  // Markdown link
  text = text.replace(
    /\[([^\]]+)\]\((https?:\/\/[^\s]+)\)/g,
    `<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>`,
  );

  // URL biasa
  text = text.replace(
    /(https?:\/\/[^\s]+)/g,
    `<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>`,
  );

  return text;
}

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

  const p = document.createElement("p");

  // 🔥 FIX UTAMA
  if (text.includes("<a ")) {
    p.innerHTML = text; // sudah HTML → langsung render
  } else {
    p.innerHTML = linkify(text); // masih teks → baru linkify
  }

  content.appendChild(p);
  li.innerHTML = avatar;
  li.appendChild(content);
  messageList.appendChild(li);

  chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });
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
        addMessage(data.Jawaban, "sender");
      } else {
        addMessage(
          "Mohon maaf saya belum yakin dengan jawaban saya 🙏 Silakan hubungi Helpdesk TI ",
          "sender",
        );
      }
    })
    .catch(() => {
      //  addMessage("Server error ❎", "sender");

      // #. Example for parsing with link
      const data = {
        text_content: "Klik di sini",
        link_url: "https://google.com",
      };

      let output;

      if (text.toLowerCase() === "hai") {
        output = `<a href="${data.link_url}" target="_blank">${data.text_content}</a>`;
      } else {
        output = data.text_content; // ❗ TANPA link
      }

      addMessage(output, "sender");
    });
}
