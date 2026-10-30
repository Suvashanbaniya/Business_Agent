
/* -------- Customer dashboard chat -------- */

const messagesContainer = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const sendButton = document.getElementById("send-button");
const chatError = document.getElementById("chat-error");

let isSending = false;

// Display a timestamp in the customer's local time
function getMessageTime() {
    return new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });
}

// Add a message to the conversation
function addMessage(text, sender) {
    const row = document.createElement("div");
    row.className = `message-row ${sender}-row`;

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = sender === "bot" ? "🤖" : "👤";

    const content = document.createElement("div");
    content.className = "message-content";

    const bubble = document.createElement("div");
    bubble.className =
        `message-bubble ${sender === "bot" ? "bot-bubble" : "user-bubble"}`;

    // Treat replies as plain text, not executable HTML
    bubble.textContent = text;

    const time = document.createElement("small");
    time.className = "message-time";
    time.textContent = getMessageTime();

    content.append(bubble, time);
    row.append(avatar, content);
    messagesContainer.appendChild(row);

    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Send a question to Flask
async function sendMessage(text) {
    const message = text.trim();

    if (!message || isSending) return;

    isSending = true;
    sendButton.disabled = true;
    chatError.hidden = true;

    addMessage(message, "user");

    const typing = document.createElement("div");
    typing.className = "typing-indicator";
    typing.textContent = "Business_Agent is typing...";
    messagesContainer.appendChild(typing);

    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
        const response = await fetch("/product-chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || data.message || "Unable to get a response."
            );
        }

        const reply = data.response ?? data.reply ?? data.answer;

        if (typeof reply !== "string" || !reply.trim()) {
            throw new Error("The server did not return an AI reply.");
        }

        addMessage(reply, "bot");

    } catch (error) {
        console.error("Customer chat error:", error);

        chatError.textContent =
            "Sorry, we couldn't get a response. " + error.message;
        chatError.hidden = false;

    } finally {
        typing.remove();
        isSending = false;
        sendButton.disabled = false;
        chatInput.focus();
    }
}

// Send using the submit button
chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const message = chatInput.value.trim();
    if (!message || isSending) return;

    chatInput.value = "";
    chatInput.style.height = "auto";

    await sendMessage(message);
});

// Enter sends, Shift + Enter adds a new line
chatInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        chatForm.requestSubmit();
    }
});

// Grow the input as the customer types
chatInput.addEventListener("input", () => {
    chatInput.style.height = "auto";
    chatInput.style.height =
        Math.min(chatInput.scrollHeight, 100) + "px";
});

// Quick question buttons
document.querySelectorAll("[data-question]").forEach((button) => {
    button.addEventListener("click", () => {
        sendMessage(button.dataset.question);
    });
});

/* -------- Sidebar navigation -------- */

// These views are placeholders until we connect real customer data.
const viewTitles = {
    orders: "My Orders",
    tickets: "My Support Tickets",
    profile: "My Profile"
};

function showView(view) {
    document.querySelectorAll(".nav-item").forEach((button) => {
        button.classList.toggle(
            "active",
            button.dataset.view === view
        );
    });

    const chatCard = document.querySelector(".chat-card");
    const rightSidebar = document.querySelector(".right-sidebar");
    const existingPlaceholder = document.querySelector(".view-placeholder");

    if (existingPlaceholder) existingPlaceholder.remove();

    if (view === "chat") {
        chatCard.hidden = false;
        rightSidebar.hidden = false;
        return;
    }

    chatCard.hidden = true;
    rightSidebar.hidden = true;

    const placeholder = document.createElement("section");
    placeholder.className = "view-placeholder";

    const title = document.createElement("h2");
    title.textContent = viewTitles[view] || "Customer Dashboard";

    const description = document.createElement("p");
    description.textContent =
        `The ${title.textContent.toLowerCase()} page needs to be connected ` +
        "to your customer database before it can display live information.";

    placeholder.append(title, description);
    document.querySelector(".main-content").appendChild(placeholder);
}

document.querySelectorAll(".nav-item, .view-all").forEach((button) => {
    button.addEventListener("click", () => {
        showView(button.dataset.view);
    });
});

// Profile button: show the profile view
document.getElementById("profile-menu").addEventListener("click", () => {
    showView("profile");
});

// Logout goes to the login page.
// Protect this route with real authentication in Flask.
document.getElementById("logout-button").addEventListener("click", () => {
    window.location.href = "/login";
});
