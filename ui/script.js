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

sendBtn.disabled = true;

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

input.addEventListener("input", () => {
  sendBtn.disabled = !input.value.trim();
});
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    if (input.value.trim()) {
      sendMessage();
      sendBtn.disabled = true;
    }
  }
});

sendBtn.addEventListener("click", () => {
  if (input.value.trim()) {
    sendMessage();
    sendBtn.disabled = true;
  }
});

function sendMessage(textFromSuggestion = null) {
  const text = textFromSuggestion || input.value.trim();
  // if (!text) {
  //   addMessage("Silakan isi pesan dulu 🙏", "sender");
  //   return;
  // }
  
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

      if (data.Status === "known") {
        addMessage(
          data.Jawaban,
          "sender",
          data.Link?.url,
          data.Link?.tag
        );
      }

      else if (data.Status === "suggestion") {
        showSuggestions(data.Suggestions);
      }

      else {
        addMessage(
          "Mohon maaf saya belum yakin dengan jawaban saya 🙏 Silakan hubungi Helpdesk TI",
          "sender"
        );
      }

    })
    .catch(() => {
       addMessage("Server error ❎", "sender");
    });
}

// SHOW SUGGESTIONS
function showSuggestions(suggestions) {

  const li = document.createElement("li");
  li.className = "sender";

  let suggestionHTML = `
    <div class="message-content">
      <p>Apakah maksud Anda salah satu dari ini?</p>
      <div class="suggestions">
  `;

  suggestions.forEach((item) => {
    suggestionHTML += `
      <button class="suggestion-btn" data-question="${item.question}">
        ${item.question}
      </button>
    `;
  });

  suggestionHTML += `
      </div>
    </div>
  `;

  li.innerHTML = `
    <img src="../img/icon-helpdesk.png">
    ${suggestionHTML}
  `;

  messageList.appendChild(li);

  li.querySelectorAll(".suggestion-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      sendMessage(btn.dataset.question);

            // disable semua tombol
      li.querySelectorAll(".suggestion-btn").forEach((b) => {
        b.disabled = true;
        b.style.opacity = "0.5";
        b.style.cursor = "not-allowed";
      });
    });
  });

  chatBody.scrollTo({
    top: chatBody.scrollHeight,
    behavior: "smooth"
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