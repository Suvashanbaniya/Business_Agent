document.addEventListener("DOMContentLoaded", function () {

    // ==================== HELPER FUNCTIONS ====================

    const $ = (selector, parent = document) =>
        parent.querySelector(selector);

    const $$ = (selector, parent = document) =>
        [...parent.querySelectorAll(selector)];

    const modal = $("#appModal");
    const modalTitle = $("#modalTitle");
    const modalBody = $("#modalBody");
    const modalForm = $("#modalForm");
    const toast = $("#toast");

    let toastTimer;
    let modalSaveCallback = null;

    function notify(message) {
        toast.textContent = message;
        toast.classList.add("show");

        clearTimeout(toastTimer);

        toastTimer = setTimeout(() => {
            toast.classList.remove("show");
        }, 2800);
    }

    function openModal(title, fields, callback, buttonText = "Save") {
        modalTitle.textContent = title;
        modalBody.innerHTML = fields;

        $("#modalSubmit").textContent = buttonText;

        modalSaveCallback = callback;

        modal.showModal();
    }

    function closeModal() {
        modal.close();
        modalSaveCallback = null;
    }

    $("#closeModal").addEventListener("click", closeModal);
    $("#cancelModal").addEventListener("click", closeModal);

    modalForm.addEventListener("submit", function (event) {
        event.preventDefault();

        if (!modalSaveCallback) {
            closeModal();
            return;
        }

        if (!modalForm.reportValidity()) {
            return;
        }

        const values = Object.fromEntries(
            new FormData(modalForm).entries()
        );

        const callback = modalSaveCallback;

        callback(values);

        closeModal();
    });


    // ==================== CREATE USER ====================

    $("#createUserBtn").addEventListener("click", function () {

        openModal(
            "Create new user",

            `
                <label class="modal-field">
                    Full name

                    <input
                        name="name"
                        required
                        placeholder="e.g. Alex Morgan"
                    >
                </label>

                <label class="modal-field">
                    Email address

                    <input
                        name="email"
                        type="email"
                        required
                        placeholder="alex@company.com"
                    >
                </label>

                <label class="modal-field">
                    User role

                    <select name="role">
                        <option>Customer</option>
                        <option>Provider</option>
                        <option>Admin</option>
                    </select>
                </label>
            `,

            function (values) {

                const name = values.name.trim();
                const email = values.email.trim();
                const role = values.role;

                const initials = name
                    .split(/\s+/)
                    .slice(0, 2)
                    .map(part => part[0])
                    .join("")
                    .toUpperCase();

                const row = document.createElement("div");

                row.className = "user-row";

                row.dataset.search =
                    `${name} ${email} ${role}`.toLowerCase();

                const avatar = document.createElement("span");
                avatar.className = "user-avatar avatar-three";
                avatar.textContent = initials;

                const details = document.createElement("div");
                details.className = "user-details";

                const userName = document.createElement("strong");
                userName.textContent = name;

                const userEmail = document.createElement("small");
                userEmail.textContent = email;

                details.append(userName, userEmail);

                const roleBadge = document.createElement("span");

                roleBadge.className =
                    "role " + role.toLowerCase();

                roleBadge.textContent = role;

                row.append(avatar, details, roleBadge);

                $("#userList").prepend(row);

                notify("User added to the dashboard preview.");
            },

            "Create user"
        );

    });


    // ==================== SEARCH ====================

    $("#globalSearch").addEventListener("input", function () {

        const query = this.value.trim().toLowerCase();

        $$("[data-search]").forEach(function (row) {

            const text = (
                row.dataset.search || row.textContent
            ).toLowerCase();

            row.hidden = !text.includes(query);

        });

    });


    // ==================== EDIT TICKET ====================

    $$(".ticket-link").forEach(function (button) {

        button.addEventListener("click", function () {

            const row = button.closest("tr");
            const cells = $$("td", row);

            const title = cells[0]
                .querySelector("small")
                .textContent;

            const category = cells[1].textContent.trim();

            const currentStatus = cells[3]
                .querySelector(".status")
                .textContent
                .replace("●", "")
                .trim();

            openModal(
                "Edit Ticket " + button.dataset.ticket,

                `
                    <label class="modal-field">
                        Ticket title

                        <input
                            name="title"
                            required
                        >
                    </label>

                    <label class="modal-field">
                        Service category

                        <select name="category">
                            <option>Service One</option>
                            <option>Service Two</option>
                            <option>Service Three</option>
                            <option>Service Four</option>
                        </select>
                    </label>

                    <label class="modal-field">
                        Ticket status

                        <select name="status">
                            <option>Completed</option>
                            <option>Pending</option>
                            <option>Active</option>
                            <option>Canceled</option>
                        </select>
                    </label>
                `,

                function (values) {

                    cells[0].querySelector("small").textContent =
                        values.title;

                    cells[1].textContent = values.category;

                    const status = document.createElement("span");

                    status.className =
                        "status " +
                        (
                            values.status === "Active"
                                ? "active-status"
                                : values.status.toLowerCase()
                        );

                    status.textContent = "● " + values.status;

                    cells[3].replaceChildren(status);

                    row.dataset.search = (
                        button.dataset.ticket + " " +
                        values.title + " " +
                        values.category + " " +
                        values.status
                    ).toLowerCase();

                    notify("Ticket updated in the dashboard preview.");

                },

                "Update ticket"
            );

            // Set the current values after the modal opens.
            $('[name="title"]', modal).value = title;
            $('[name="category"]', modal).value = category;
            $('[name="status"]', modal).value = currentStatus;

        });

    });


    // ==================== SIDEBAR NAVIGATION ====================

    $$(".nav-item[data-view]").forEach(function (link) {

        link.addEventListener("click", function (event) {

            event.preventDefault();

            const view = link.dataset.view;

            $$(".nav-item").forEach(function (item) {

                item.classList.toggle(
                    "active",
                    item.dataset.view === view
                );

            });

            $("#sidebar").classList.remove("open");

            if (view === "Dashboard") {

                $("#dashboard").scrollIntoView({
                    behavior: "smooth"
                });

            } else {

                notify(
                    view +
                    " is currently a dashboard preview. " +
                    "Connect it to a Flask route to open a real page."
                );

            }

        });

    });


    // ==================== MOBILE SIDEBAR ====================

    $("#mobileMenu").addEventListener("click", function () {

        $("#sidebar").classList.toggle("open");

    });


    // ==================== MESSAGES ====================

    $("#messagesBtn").addEventListener("click", function () {

        notify("You have 2 unread messages.");

    });


    // ==================== NOTIFICATIONS ====================

    $("#notificationsBtn").addEventListener("click", function () {

        notify("You're all caught up on notifications.");

    });


    // ==================== PROFILE ====================

    $("#profileBtn").addEventListener("click", function () {

        notify("Signed in as Mariana (demo profile).");

    });


    // ==================== DATE CONTROLS ====================

    $("#customDate").addEventListener("click", function () {

        $("#startDate").focus();

        notify(
            "Select your start and end dates, then press the calendar button."
        );

    });


    $("#applyDate").addEventListener("click", function () {

        const start = $("#startDate").value;
        const end = $("#endDate").value;

        if (!start || !end) {
            notify("Please select both dates.");
            return;
        }

        if (start > end) {
            notify("The start date must be before the end date.");
            return;
        }

        notify(
            "Date range selected: " +
            start + " to " + end +
            ". Connect a Flask query to filter real data."
        );

    });


    // ==================== DISTRIBUTION DROPDOWN ====================

    $("#distributionRange").addEventListener("change", function () {

        notify("Selected distribution range: " + this.value);

    });


    // ==================== TICKET CHART ====================

    if (typeof Chart !== "undefined") {

        const ctx = $("#ticketChart").getContext("2d");

        const gradient = ctx.createLinearGradient(0, 0, 0, 210);

        gradient.addColorStop(
            0,
            "rgba(81, 69, 229, 0.10)"
        );

        gradient.addColorStop(
            1,
            "rgba(81, 69, 229, 0)"
        );

        const chart = new Chart(ctx, {

            type: "line",

            data: {

                labels: [
                    "Feb", "Mar", "Apr", "May",
                    "Jun", "Jul", "Aug", "Sep",
                    "Oct", "Nov", "Dec", "Jan"
                ],

                datasets: [

                    {
                        label: "New Ticket",

                        data: [
                            20, 25, 19, 36,
                            34, 42, 40, 38,
                            55, 51, 59, 57
                        ],

                        borderColor: "#5145E5",
                        backgroundColor: gradient,

                        fill: true,
                        tension: 0.42,
                        borderWidth: 2,

                        pointRadius: 0,
                        pointHoverRadius: 4
                    },

                    {
                        label: "Completed Ticket",

                        data: [
                            15, 12, 16, 21,
                            24, 28, 31, 26,
                            24, 29, 40, 36
                        ],

                        borderColor: "#9B9AF2",
                        backgroundColor: "transparent",

                        fill: false,
                        tension: 0.42,
                        borderWidth: 2,

                        pointRadius: 0,
                        pointHoverRadius: 4
                    }

                ]

            },

            options: {

                responsive: true,
                maintainAspectRatio: false,

                interaction: {
                    intersect: false,
                    mode: "index"
                },

                plugins: {

                    legend: {
                        display: false
                    },

                    tooltip: {
                        backgroundColor: "#29283A",
                        padding: 10
                    }

                },

                scales: {

                    x: {

                        grid: {
                            display: false
                        },

                        border: {
                            display: false
                        },

                        ticks: {
                            color: "#8E8E98",
                            font: {
                                family: "Inter",
                                size: 10
                            }
                        }

                    },

                    y: {

                        grid: {
                            color: "#F1F1F4"
                        },

                        border: {
                            display: false
                        },

                        ticks: {
                            display: false
                        },

                        beginAtZero: true

                    }

                }

            }

        });


        // Toggle chart series using the legend buttons.
        $$(".legend-button").forEach(function (button) {

            button.addEventListener("click", function () {

                const index = Number(button.dataset.series);

                const visible = chart.isDatasetVisible(index);

                chart.setDatasetVisibility(index, !visible);

                chart.update();

                button.classList.toggle("disabled", visible);

            });

        });

    } else {

        notify(
            "The chart library could not load. Check your internet connection."
        );

    }

});


// -------- Floating AI chatbot --------

const chatToggle = document.getElementById("ai-chat-toggle");
const chatPanel = document.getElementById("ai-chat-panel");
const chatClose = document.getElementById("ai-chat-close");
const chatForm = document.getElementById("ai-chat-form");
const chatInput = document.getElementById("ai-chat-input");
const chatMessages = document.getElementById("ai-chat-messages");
const chatSend = document.getElementById("ai-chat-send");
const chatError = document.getElementById("ai-chat-error");

// Open or close the chat panel
function toggleAIChat(forceOpen = null) {
    const shouldOpen = forceOpen ?? chatPanel.hidden;

    chatPanel.hidden = !shouldOpen;
    chatToggle.setAttribute("aria-expanded", String(shouldOpen));
    chatToggle.setAttribute(
        "aria-label",
        shouldOpen ? "Close AI assistant" : "Open AI assistant"
    );

    document.getElementById("ai-chat-toggle-icon").textContent =
        shouldOpen ? "×" : "✦";

    if (shouldOpen) {
        chatInput.focus();
    }
}

chatToggle.addEventListener("click", () => toggleAIChat());
chatClose.addEventListener("click", () => toggleAIChat(false));

// Create a message safely without interpreting it as HTML
function addAIMessage(message, sender) {
    const messageContainer = document.createElement("div");
    messageContainer.className =
        sender === "user"
            ? "ai-message ai-message-user"
            : "ai-message ai-message-bot";

    const bubble = document.createElement("div");
    bubble.className = "ai-message-bubble";
    bubble.textContent = message; // Prevents user text from being treated as HTML

    const label = document.createElement("span");
    label.className = "ai-message-time";
    label.textContent = sender === "user" ? "You" : "AI Assistant";

    messageContainer.append(bubble, label);
    chatMessages.appendChild(messageContainer);

    // Automatically scroll to the latest message
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageContainer;
}

// Send a message to the Flask backend
chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const message = chatInput.value.trim();

    if (!message || chatSend.disabled) {
        return;
    }

    addAIMessage(message, "user");

    chatInput.value = "";
    chatInput.style.height = "auto";
    chatSend.disabled = true;
    chatError.hidden = true;

    const typing = document.createElement("div");
    typing.className = "ai-typing";
    typing.textContent = "AI is thinking...";
    chatMessages.appendChild(typing);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch("/chat", {
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
                data.error || data.message || "The server could not process your message."
            );
        }

        // Accept common response field names from Flask
        const reply = data.response ?? data.reply ?? data.answer;

        if (typeof reply !== "string" || !reply.trim()) {
            throw new Error(
                "No reply was returned. Check the JSON response from your Flask /chat endpoint."
            );
        }

        addAIMessage(reply, "bot");

    } catch (error) {
        console.error("AI chatbot error:", error);

        chatError.textContent =
            error.message || "Unable to connect to the AI assistant.";
        chatError.hidden = false;

    } finally {
        typing.remove();
        chatSend.disabled = false;
        chatInput.focus();
    }
});

// Press Enter to send; Shift + Enter inserts a new line
chatInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        chatForm.requestSubmit();
    }
});

// Automatically grow the input as the admin types
chatInput.addEventListener("input", () => {
    chatInput.style.height = "auto";
    chatInput.style.height =
        Math.min(chatInput.scrollHeight, 100) + "px";
});