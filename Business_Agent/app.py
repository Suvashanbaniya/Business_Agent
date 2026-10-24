
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from ai.llm import ask_llm
from services.create_ticket import create_ticket

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}

    user_message = data.get("message", "")
    customer_id = data.get("customer_id")

    # Make sure the message is valid text.
    if not isinstance(user_message, str) or not user_message.strip():
        return jsonify({
            "response": "Please enter a message.",
            "status": "error"
        }), 400

    user_message = user_message.strip()

    print("\nCustomer:", user_message)

    # Check whether the customer explicitly requests a ticket.
    message_lower = user_message.lower()

    ticket_keywords = [
        "create a ticket",
        "create ticket",
        "open a ticket",
        "open ticket",
        "raise a ticket",
        "raise ticket",
        "report an issue",
        "report a problem",
        "submit a complaint",
        "log a complaint"
    ]

    wants_ticket = any(
        keyword in message_lower
        for keyword in ticket_keywords
    )

    # Create a ticket only when the customer requests one.
    if wants_ticket:

        # A customer ID is required for ticket creation.
        if customer_id is None:
            return jsonify({
                "response": (
                    "Please sign in to your account before "
                    "creating a support ticket."
                ),
                "status": "error"
            }), 400

        # Accept only a positive integer customer ID.
        # Reject booleans, strings, zero, and negative numbers.
        if (
            isinstance(customer_id, bool)
            or not isinstance(customer_id, int)
            or customer_id <= 0
        ):
            return jsonify({
                "response": "A valid customer ID is required.",
                "status": "error"
            }), 400

        # Remove ticket-request phrases to form a basic title.
        issue_title = user_message

        for keyword in ticket_keywords:
            issue_title = issue_title.replace(keyword, "")

        issue_title = issue_title.strip(" .,:-")

        if not issue_title:
            issue_title = "Customer support request"

        # Keep the title short enough to be readable.
        issue_title = issue_title[:100]

        try:
            # Create the ticket using the existing service.
            ticket_id = create_ticket(
                customer_id,
                issue_title,
                user_message
            )

            reply = (
                f"Your support ticket #{ticket_id} "
                "has been created successfully. "
                "Our support team can review your issue."
            )

            print("Ticket created:", ticket_id)

            return jsonify({
                "response": reply,
                "status": "success",
                "ticket_id": ticket_id,
                "ticket_status": "Open",
                "model": "llama3"
            }), 201

        except ValueError:
            # The ticket service raises ValueError if the
            # specified customer does not exist.
            return jsonify({
                "response": (
                    "We couldn't verify your customer account. "
                    "Please check your account and try again."
                ),
                "status": "error"
            }), 400

        except Exception:
            # Log the technical error on the server.
            app.logger.exception("Failed to create support ticket")

            return jsonify({
                "response": (
                    "Sorry, we couldn't create your support ticket "
                    "right now. Please try again later."
                ),
                "status": "error"
            }), 500

    # If no ticket was requested, use the normal AI chatbot.
    try:
        reply = ask_llm(user_message)

        print("AI:", reply)

        return jsonify({
            "response": reply,
            "status": "success",
            "model": "llama3"
        })

    except Exception:
        app.logger.exception("Chatbot request failed")

        return jsonify({
            "response": (
                "Sorry, I'm having trouble responding right now. "
                "Please try again later."
            ),
            "status": "error"
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
