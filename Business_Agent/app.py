
import os
import sqlite3
from pathlib import Path
from functools import wraps
from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    session,
    flash,
)
from flask_cors import CORS
from werkzeug.security import check_password_hash

from ai.llm import ask_llm
from services.create_ticket import create_ticket

app = Flask(__name__)
CORS(app)
# Locate auth.db relative to app.py.
AUTH_DB_PATH = (
    Path(__file__).resolve().parent
    / "database"
    / "auth.db"
)

# Set this environment variable before starting Flask.
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

if not app.secret_key:
    raise RuntimeError(
        "Set the FLASK_SECRET_KEY environment variable before running Flask."
    )

# Basic protection for the session cookie.
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

def login_required(view_function):
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        # Redirect unauthenticated users to the login page.
        if "user_id" not in session:
            if request.path == "/chat":
                return jsonify({
                    "response": "Please log in to continue.",
                    "status": "error"
                }), 401

            return redirect(url_for("login"))

        return view_function(*args, **kwargs)

    return wrapper
@app.route("/")
@login_required
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json(silent=True) or {}

    user_message = data.get("message", "")
   # Get the customer ID from the verified login session.
    customer_id = session.get("customer_id")

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

    # Only customer accounts can create support tickets.
    if wants_ticket and session.get("role") != "customer":
        return jsonify({
            "response": "Only customer accounts can create support tickets.",
            "status": "error"
        }), 403

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


@app.route("/login", methods=["GET", "POST"])
def login():
    # Display the login page when the user first visits.
    if request.method == "GET":
        return render_template("login.html")

    # Read the submitted login credentials.
    login_id = request.form.get("login_id", "").strip()
    password = request.form.get("password", "")

    if not login_id or not password:
        flash("Please enter your login ID and password.")
        return redirect(url_for("login"))

    # Look up the account in the authentication database.
    with sqlite3.connect(AUTH_DB_PATH) as connection:
        connection.row_factory = sqlite3.Row

        user = connection.execute(
            """
            SELECT user_id, login_id, password_hash, role, customer_id
            FROM users
            WHERE login_id = ?
            """,
            (login_id,)
        ).fetchone()

    # Use the same message for an unknown ID and wrong password.
    if user is None or not check_password_hash(
        user["password_hash"], password
    ):
        flash("Invalid login ID or password.")
        return redirect(url_for("login"))

    # Start a fresh session after successful authentication.
    session.clear()
    session["user_id"] = user["user_id"]
    session["login_id"] = user["login_id"]
    session["role"] = user["role"]

    if user["role"] == "customer":
        session["customer_id"] = user["customer_id"]

    # For now, both roles go to the existing homepage.
    return redirect(url_for("home"))


@app.route("/logout", methods=["POST"])
def logout():
    # Remove the logged-in user's session data.
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
