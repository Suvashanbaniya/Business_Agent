/* ================= CHAT ELEMENTS ================= */

const chatBox = document.getElementById("chat-box");
const input = document.getElementById("message");


/* ================= ADD MESSAGE ================= */

function addMessage(text, sender) {

    const row = document.createElement("div");

    row.className =
        sender === "user"
            ? "message-row user-row"
            : "message-row bot-row";


    /* Avatar */

    const avatar = document.createElement("div");

    avatar.className =
        sender === "user"
            ? "avatar user-avatar"
            : "avatar bot-avatar";


    avatar.innerText =
        sender === "user"
            ? "You"
            : "🤖";


    /* Message wrapper */

    const wrapper = document.createElement("div");

    wrapper.className = "message-wrapper";


    /* Message information */

    const meta = document.createElement("div");

    meta.className = "message-meta";


    const name = document.createElement("strong");

    name.innerText =
        sender === "user"
            ? "You"
            : "AI Assistant";


    const time = document.createElement("span");

    time.innerText = getCurrentTime();


    meta.appendChild(name);

    meta.appendChild(time);


    /* Message */

    const message = document.createElement("div");

    message.className =
        sender === "user"
            ? "message user-message"
            : "message bot-message";


    message.innerText = text;


    /* Build structure */

    wrapper.appendChild(meta);

    wrapper.appendChild(message);


    row.appendChild(avatar);

    row.appendChild(wrapper);


    chatBox.appendChild(row);


    /* Scroll to latest message */

    chatBox.scrollTop = chatBox.scrollHeight;

}


/* ================= CURRENT TIME ================= */

function getCurrentTime() {

    const now = new Date();

    return now.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });

}


/* ================= SEND MESSAGE ================= */

async function sendMessage() {

    const text = input.value.trim();


    /* Don't send empty messages */

    if (text === "") {
        return;
    }


    /* Show user's message */

    addMessage(text, "user");


    /* Clear input */

    input.value = "";


    /* Disable input while waiting */

    input.disabled = true;


    try {


        /* Send message to Flask */

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: text
            })

        });


        /* Check HTTP response */

        if (!response.ok) {

            throw new Error(
                "Server returned " + response.status
            );

        }


        /* Convert response to JSON */

        const data = await response.json();


        /* Display AI response */

        addMessage(
            data.response,
            "bot"
        );


    }


    catch (error) {


        console.log(error);


        addMessage(
            "Sorry, I cannot connect to the AI server.",
            "bot"
        );


    }


    finally {

        /* Enable input again */

        input.disabled = false;

        input.focus();

    }

}


/* ================= ENTER KEY ================= */

input.addEventListener("keydown", function(event) {


    /*
        Enter = send

        Shift + Enter = new line
    */

    if (
        event.key === "Enter" &&
        !event.shiftKey
    ) {

        event.preventDefault();

        sendMessage();

    }

});


/* ================= NEW CHAT ================= */

function newChat() {


    /*
        Keep the date divider
        and remove previous messages.
    */

    chatBox.innerHTML = `

        <div class="date-divider">

            <span>Today</span>

        </div>

    `;


    addMessage(
        "Hello! I'm your AI assistant. How can I help you today?",
        "bot"
    );


    input.focus();

}


/* ================= ATTACH FILE ================= */

function attachFile() {

    alert(
        "File attachment will be added later."
    );

}


/* ================= EMOJI ================= */

function addEmoji() {

    input.value += " 😊";

    input.focus();

}


/* ================= MOBILE SIDEBAR ================= */

function toggleSidebar() {

    const sidebar =
        document.querySelector(".sidebar");


    sidebar.classList.toggle("show");

}