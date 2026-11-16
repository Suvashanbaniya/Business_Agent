
import os
import sqlite3
from pathlib import Path
from functools import wraps
import secrets
import hmac
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session
import smtplib
from email.message import EmailMessage
# -------- Load environment variables
BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")
import hashlib
from datetime import datetime, timedelta, timezone
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
from werkzeug.security import check_password_hash, generate_password_hash
from ai.intent_detector import detect_intent
from ai.llm import ask_llm
from services.create_ticket import create_ticket , get_customer_tickets
from services.ticket_message_service import (
    add_ticket_message,
    get_ticket_messages
)
from ai.customer_chat import product_chat_response

# -------- Load environment variables
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")



# -------- Send OTP Email
def send_otp_email(receiver_email, otp):

    email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    message = EmailMessage()

    message["Subject"] = "Business Agent - Password Reset OTP"
    message["From"] = email
    message["To"] = receiver_email

    message.set_content(f"""
Hello,

Your Business Agent password reset OTP is:

{otp}

This OTP expires in 5 minutes.

If you did not request this, ignore this email.

Business Agent Team
""")

    # Connect to Gmail SMTP.
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(email, password)
        server.send_message(message)

    return True

app = Flask(__name__)
CORS(app)


# Configure Flask session security.
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "Suvashan_BusinessAgent_DevKey_2026"
)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
# Locate auth.db relative to app.py.
AUTH_DB_PATH = (
    Path(__file__).resolve().parent
    / "database"
    / "auth.db"
)

# -------- Create password reset table
def initialize_password_reset_table():

    with sqlite3.connect(AUTH_DB_PATH) as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                token_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash TEXT NOT NULL UNIQUE,
                expires_at TEXT NOT NULL,
                used INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        connection.commit()
  
# -------- Initialize Password Reset OTP Table
def initialize_password_reset_otp_table():

    with sqlite3.connect(AUTH_DB_PATH) as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS password_reset_otps (

                otp_id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                otp_hash TEXT NOT NULL,

                expires_at TEXT NOT NULL,

                used INTEGER NOT NULL DEFAULT 0,

                attempts INTEGER NOT NULL DEFAULT 0,

                created_at TEXT NOT NULL,

                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        connection.commit()      
# Locate customer.db relative to app.py.
CUSTOMER_DB_PATH = (
    Path(__file__).resolve().parent
    / "database"
    / "customer.db"
)
# -------- Unified customer chatbot API
@app.route("/product-chat", methods=["POST"])
def product_chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    # -------- Validate the incoming message
    if not isinstance(message, str) or not message.strip():
        return jsonify({
            "response": "Please enter a message.",
            "status": "error"
        }), 400

    message = message.strip()

    try:
        # -------- Detect the customer's intent
        intent_result = detect_intent(message)
        intent = intent_result["intent"]

        print("Detected intent:", intent)

        # -------- Handle existing support ticket status requests
        if intent == "ticket_status":
            # Only logged-in customers can access their tickets.
            if session.get("role") != "customer":
                return jsonify({
                    "response": (
                        "Please sign in to your customer account "
                        "so I can check your support tickets."
                    ),
                    "status": "login_required"
                }), 401

            customer_id = session.get("customer_id")

            # Retrieve tickets belonging to this customer only.
            tickets = get_customer_tickets(customer_id)

            if not tickets:
                return jsonify({
                    "response": "You don't have any support tickets yet.",
                    "status": "success"
                }), 200

            # Display the customer's existing tickets.
            ticket_messages = []

            for ticket in tickets:
                ticket_messages.append(
                    f"Ticket #{ticket[0]}: {ticket[2]}\n"
                    f"Status: {ticket[4]}\n"
                    f"Created: {ticket[5]}"
                )

            return jsonify({
                "response": (
                    "Here are your support tickets:\n\n"
                    + "\n\n".join(ticket_messages)
                ),
                "status": "success",
                "tickets": [
                    {
                        "ticket_id": ticket[0],
                        "issue_title": ticket[2],
                        "status": ticket[4],
                        "created_at": ticket[5]
                    }
                    for ticket in tickets
                ]
            }), 200

        # -------- Handle complaints and refund requests
        if intent in ["complaint", "refund_request"]:
            # Only logged-in customers can create tickets.
            if session.get("role") != "customer":
                return jsonify({
                    "response": (
                        "I'm sorry to hear about this. "
                        "Please sign in to your customer account "
                        "so I can create a support ticket for you."
                    ),
                    "status": "login_required"
                }), 401

            customer_id = session.get("customer_id")

            # Validate the customer ID from the session.
            if (
                isinstance(customer_id, bool)
                or not isinstance(customer_id, int)
                or customer_id <= 0
            ):
                return jsonify({
                    "response": "We couldn't verify your customer account. Please sign in again.",
                    "status": "error"
                }), 400

            # Generate a ticket title based on the intent.
            if intent == "refund_request":
                issue_title = "Customer refund request"
            else:
                issue_title = "Customer complaint"

            # Create the support ticket.
            ticket_id = create_ticket(
                customer_id,
                issue_title,
                message
            )

            return jsonify({
                "response": (
                    f"Your support ticket #{ticket_id} "
                    "has been created successfully. "
                    "Our support team can review your issue."
                ),
                "status": "success",
                "ticket_id": ticket_id,
                "ticket_status": "Open"
            }), 201

        # -------- Handle product questions publicly
        answer = product_chat_response(message)

        return jsonify({
            "response": answer,
            "status": "success",
            "model": "llama3"
        })

    except Exception:
        app.logger.exception("Customer chatbot request failed")

        return jsonify({
            "response": (
                "Sorry, I'm having trouble responding right now. "
                "Please try again later."
            ),
            "status": "error"
        }), 500
        
    

@app.route("/register", methods=["GET", "POST"])
def register():

    # Display the registration form.
    if request.method == "GET":
        return render_template("register.html")

    # Get information submitted through the registration form.
    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    phone = request.form.get("phone", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    # Validate required fields.
    if not full_name or not email or not password or not confirm_password:
        flash("Please fill in all required fields.")
        return redirect(url_for("register"))

    # Basic email validation.
    if "@" not in email or "." not in email.split("@")[-1]:
        flash("Please enter a valid email address.")
        return redirect(url_for("register"))

    # Validate password.
    if len(password) < 8:
        flash("Password must contain at least 8 characters.")
        return redirect(url_for("register"))

    if password != confirm_password:
        flash("Passwords do not match.")
        return redirect(url_for("register"))

    # Check whether the email already exists in customers.
    with sqlite3.connect(CUSTOMER_DB_PATH) as connection:
        existing_customer = connection.execute(
            """
            SELECT customer_id
            FROM customers
            WHERE LOWER(email) = ?
            """,
            (email,)
        ).fetchone()

    if existing_customer:
        flash("An account with this email already exists.")
        return redirect(url_for("register"))

    # Email is also used as the login ID.
    with sqlite3.connect(AUTH_DB_PATH) as connection:
        existing_user = connection.execute(
            """
            SELECT user_id
            FROM users
            WHERE LOWER(login_id) = ?
            """,
            (email,)
        ).fetchone()

    if existing_user:
        flash("This email is already associated with an account.")
        return redirect(url_for("register"))

    # Hash the password before storing it.
    password_hash = generate_password_hash(password)

    customer_id = None

    try:
        # First, create the customer record.
        with sqlite3.connect(CUSTOMER_DB_PATH) as connection:
            cursor = connection.execute(
                """
                INSERT INTO customers (full_name, email, phone)
                VALUES (?, ?, ?)
                """,
                (full_name, email, phone or None)
            )

            customer_id = cursor.lastrowid

        # Then, create the login account linked to that customer.
        with sqlite3.connect(AUTH_DB_PATH) as connection:
            connection.execute(
                """
                INSERT INTO users (
                    login_id,
                    password_hash,
                    role,
                    customer_id
                )
                VALUES (?, ?, ?, ?)
                """,
                (email, password_hash, "customer", customer_id)
            )

    except sqlite3.IntegrityError:
        # If account creation fails, remove the customer record
        # created in the first database.
        if customer_id is not None:
            with sqlite3.connect(CUSTOMER_DB_PATH) as connection:
                connection.execute(
                    "DELETE FROM customers WHERE customer_id = ?",
                    (customer_id,)
                )

        flash("Unable to create your account. Please check your details.")
        return redirect(url_for("register"))

    flash("Your account has been created successfully. Please log in.")
    return redirect(url_for("login"))


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
# -------- Public customer homepage
@app.route("/")
def home():
    return render_template("customer.html")

# -------- Admin dashboard
@app.route("/admin")
@login_required
def admin_dashboard():

    # Only admins can access the admin dashboard.
    if session.get("role") != "admin":
        return redirect(url_for("home"))

    return render_template("admin.html")



# -------- Admin: Retrieve all customer support tickets
@app.route("/admin/api/tickets", methods=["GET"])
@login_required
def get_all_tickets():

    # Only administrators can access all customer tickets.
    if session.get("role") != "admin":
        return jsonify({
            "status": "error",
            "response": "Access denied. Admin privileges required."
        }), 403

    try:
        with sqlite3.connect(CUSTOMER_DB_PATH) as conn:

            # Retrieve tickets together with their customer information.
            conn.row_factory = sqlite3.Row

            cursor = conn.execute("""
                SELECT
                    t.ticket_id,
                    t.customer_id,
                    c.full_name,
                    c.email,
                    c.phone,
                    t.issue_title,
                    t.issue_description,
                    t.status,
                    t.created_at

                FROM support_tickets AS t

                INNER JOIN customers AS c
                    ON t.customer_id = c.customer_id

                ORDER BY t.created_at DESC
            """)

            tickets = [dict(row) for row in cursor.fetchall()]

        return jsonify({
            "status": "success",
            "total_tickets": len(tickets),
            "tickets": tickets
        }), 200

    except Exception:
        app.logger.exception("Failed to retrieve admin tickets")

        return jsonify({
            "status": "error",
            "response": "Unable to retrieve tickets."
        }), 500


@app.route("/admin/api/tickets/<int:ticket_id>/messages", methods=["GET"])
@login_required
def get_admin_ticket_messages(ticket_id):

    # Only admins can access this endpoint
    if session.get("role") != "admin":
        return jsonify({
            "status": "error",
            "response": "Admin privileges required."
        }), 403

    try:
        with sqlite3.connect(CUSTOMER_DB_PATH) as conn:

            conn.row_factory = sqlite3.Row

            # Retrieve the ticket details
            cursor = conn.execute(
                """
                SELECT
                    t.ticket_id,
                    t.customer_id,
                    c.full_name,
                    c.email,
                    t.issue_title,
                    t.issue_description,
                    t.status,
                    t.created_at
                FROM support_tickets AS t
                INNER JOIN customers AS c
                    ON t.customer_id = c.customer_id
                WHERE t.ticket_id = ?
                """,
                (ticket_id,)
            )

            ticket = cursor.fetchone()

            if ticket is None:
                return jsonify({
                    "status": "error",
                    "response": "Ticket not found."
                }), 404

        # Retrieve the ticket conversation
        messages = get_ticket_messages(ticket_id)

        return jsonify({
            "status": "success",
            "ticket": dict(ticket),
            "messages": messages
        }), 200

    except Exception:
        app.logger.exception("Failed to retrieve ticket details")

        return jsonify({
            "status": "error",
            "response": "Unable to retrieve ticket details."
        }), 500

@app.route(
    "/admin/api/tickets/<int:ticket_id>/messages",
    methods=["POST"]
)
@login_required
def send_admin_ticket_message(ticket_id):

    # Only admins can send replies
    if session.get("role") != "admin":
        return jsonify({
            "status": "error",
            "response": "Admin privileges required."
        }), 403

    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "status": "error",
            "response": "Message cannot be empty."
        }), 400

    try:
        message_id = add_ticket_message(
            ticket_id=ticket_id,
            sender_id=session["user_id"],
            sender_role="admin",
            message=message
        )

        return jsonify({
            "status": "success",
            "response": "Reply sent successfully.",
            "message_id": message_id
        }), 201

    except ValueError as error:
        return jsonify({
            "status": "error",
            "response": str(error)
        }), 404

    except Exception:
        app.logger.exception("Failed to send admin ticket reply")

        return jsonify({
            "status": "error",
            "response": "Unable to send reply."
        }), 500


# -------- Admin: Update support ticket status
@app.route("/admin/api/tickets/<int:ticket_id>", methods=["PUT"])
@login_required
def update_admin_ticket(ticket_id):

    # Only administrators can update ticket status.
    if session.get("role") != "admin":
        return jsonify({
            "status": "error",
            "response": "Admin privileges required."
        }), 403

    data = request.get_json(silent=True) or {}
    new_status = data.get("status")

    # Only allow these three ticket statuses.
    allowed_statuses = ["Open", "In Progress", "Resolved"]

    if new_status not in allowed_statuses:
        return jsonify({
            "status": "error",
            "response": "Invalid ticket status."
        }), 400

    try:
        with sqlite3.connect(CUSTOMER_DB_PATH) as conn:

            cursor = conn.execute(
                """
                UPDATE support_tickets
                SET status = ?
                WHERE ticket_id = ?
                """,
                (new_status, ticket_id)
            )

            if cursor.rowcount == 0:
                return jsonify({
                    "status": "error",
                    "response": "Ticket not found."
                }), 404

            conn.commit()

        return jsonify({
            "status": "success",
            "response": "Ticket status updated successfully.",
            "ticket_id": ticket_id,
            "new_status": new_status
        }), 200

    except Exception:
        app.logger.exception("Failed to update ticket status")

        return jsonify({
            "status": "error",
            "response": "Unable to update ticket status."
        }), 500

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
    
    
    
    # Identify what the customer wants.
    intent_result = detect_intent(user_message)

    intent = intent_result["intent"]
    confidence = intent_result["confidence"]
    needs_human = intent_result["needs_human"]

    print("Detected intent:", intent)
    print("Confidence:", confidence)
    print("Needs human review:", needs_human)
    # Create a ticket for complaints and refund requests.
    wants_ticket = intent in ["complaint", "refund_request"]

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

        # Generate a title based on the detected intent.
        if intent == "refund_request":
            issue_title = "Customer refund request"
        else:
            issue_title = "Customer complaint"

        # Keep the original message as the ticket description.
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
    # Route product enquiries to the product chatbot.
    if intent == "product_inquiry":
        try:
            reply = product_chat_response(user_message, customer_id)

            return jsonify({
                "response": reply,
                "status": "success",
                "model": "llama3"
            })

        except Exception:
            app.logger.exception("Product chatbot request failed")

            return jsonify({
                "response": "Sorry, I couldn't retrieve product information right now.",
                "status": "error"
            }), 500

    # Handle other messages with the normal AI chatbot.
    # -------- Get the authenticated customer's email

    customer_email = None

    if customer_id is not None:
        with sqlite3.connect(CUSTOMER_DB_PATH) as connection:
            customer = connection.execute(
                """
                SELECT email
                FROM customers
                WHERE customer_id = ?
                """,
                (customer_id,)
            ).fetchone()

        if customer:
            customer_email = customer[0]

    # -------- Temporary debugging
    print("Logged-in customer ID:", customer_id)
    print("Customer email found:", customer_email)

    # -------- Handle other messages with the normal AI chatbot
    try:
        reply = ask_llm(user_message, customer_email)

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


# -------- Get tickets belonging to the logged-in customer
@app.route("/my-tickets", methods=["GET"])
@login_required
def my_tickets():

    # Only customer accounts can access their tickets.
    if session.get("role") != "customer":
        return jsonify({
            "response": "Access denied.",
            "status": "error"
        }), 403

    customer_id = session.get("customer_id")

    # Validate the customer ID.
    if (
        isinstance(customer_id, bool)
        or not isinstance(customer_id, int)
        or customer_id <= 0
    ):
        return jsonify({
            "response": "Invalid customer account.",
            "status": "error"
        }), 400

    try:
        tickets = get_customer_tickets(customer_id)

        # Convert database records into JSON-friendly objects.
        ticket_list = []

        for ticket in tickets:
            ticket_list.append({
                "ticket_id": ticket[0],
                "customer_id": ticket[1],
                "issue_title": ticket[2],
                "issue_description": ticket[3],
                "status": ticket[4],
                "created_at": ticket[5]
            })

        return jsonify({
            "status": "success",
            "tickets": ticket_list
        }), 200

    except Exception:
        app.logger.exception("Failed to retrieve customer tickets")

        return jsonify({
            "response": "Unable to retrieve your tickets right now.",
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
    # -------- Send each role to its correct interface
    if user["role"] == "admin":
        return redirect(url_for("admin_dashboard"))

    return redirect(url_for("home"))


# -------- Forgot Password
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        login_id = request.form.get("login_id", "").strip()

        # Clear any previous password-reset session.
        session.pop("password_reset_user_id", None)

        with sqlite3.connect(AUTH_DB_PATH) as connection:
            connection.row_factory = sqlite3.Row

            user = connection.execute(
                "SELECT user_id FROM users WHERE login_id = ?",
                (login_id,)
            ).fetchone()

            if user:
                try:
                    # Generate and store a new six-digit OTP.
                    otp = generate_password_reset_otp(user["user_id"])

                    # Send the OTP to the user's email.
                    send_otp_email(login_id, otp)

                    # Remember which user is completing password reset.
                    session["password_reset_user_id"] = user["user_id"]

                    print("RESET USER ID:", session.get("password_reset_user_id"))

                except Exception as error:
                    print("OTP sending error:", error)

                    flash("Unable to send OTP. Please try again.", "danger")
                    return redirect(url_for("forgot_password"))

            else:
                print("User not found:", login_id)

                flash(
                    "This email is not registered. Please create an account or check your email.",
                    "danger"
                )
                return redirect(url_for("forgot_password"))

            flash("OTP sent successfully. Check your email.", "success")

            return redirect(url_for("verify_password_reset_otp"))


# -------- Verify Password Reset OTP
@app.route("/verify-otp", methods=["GET", "POST"])
def verify_password_reset_otp():

    user_id = session.get("password_reset_user_id")
    print("VERIFY SESSION:", dict(session))
    print("VERIFY USER ID:", user_id)
    if not user_id:
        flash("Please request a password reset first.", "warning")
        return redirect(url_for("verify_password_reset_otp"))

    if request.method == "POST":

        entered_otp = request.form.get("otp", "").strip()

        # OTP must contain exactly six digits.
        if not entered_otp.isdigit() or len(entered_otp) != 6:
            flash("Enter a valid six-digit OTP.", "danger")
            return redirect(url_for("verify_password_reset_otp"))

        with sqlite3.connect(AUTH_DB_PATH) as connection:
            connection.row_factory = sqlite3.Row

            otp_record = connection.execute(
                """
                SELECT *
                FROM password_reset_otps
                WHERE user_id = ? AND used = 0
                ORDER BY otp_id DESC
                LIMIT 1
                """,
                (user_id,)
            ).fetchone()

            if not otp_record:
                flash("Invalid or expired OTP. Request a new one.", "danger")
                return redirect(url_for("forgot_password"))

            # Check whether the OTP has expired.
            expires_at = datetime.fromisoformat(otp_record["expires_at"])

            if datetime.now(timezone.utc) >= expires_at:
                connection.execute(
                    "UPDATE password_reset_otps SET used = 1 WHERE otp_id = ?",
                    (otp_record["otp_id"],)
                )
                connection.commit()

                flash("Your OTP has expired. Request a new one.", "danger")
                return redirect(url_for("forgot_password"))

            # Check the maximum number of attempts.
            if otp_record["attempts"] >= 5:
                connection.execute(
                    "UPDATE password_reset_otps SET used = 1 WHERE otp_id = ?",
                    (otp_record["otp_id"],)
                )
                connection.commit()

                flash("Too many attempts. Request a new OTP.", "danger")
                return redirect(url_for("forgot_password"))

            # Hash the entered OTP and compare it with the stored hash.
            entered_hash = hashlib.sha256(
                entered_otp.encode()
            ).hexdigest()

            if not hmac.compare_digest(
                entered_hash,
                otp_record["otp_hash"]
            ):
                connection.execute(
                    """
                    UPDATE password_reset_otps
                    SET attempts = attempts + 1
                    WHERE otp_id = ?
                    """,
                    (otp_record["otp_id"],)
                )
                connection.commit()

                flash("Incorrect OTP. Please try again.", "danger")
                return redirect(url_for("verify_password_reset_otp"))

            # OTP is correct. Mark it as used.
            connection.execute(
                "UPDATE password_reset_otps SET used = 1 WHERE otp_id = ?",
                (otp_record["otp_id"],)
            )
            connection.commit()

        # Allow this user to proceed to the password reset page.
        session["password_reset_verified"] = True

        flash("OTP verified successfully.", "success")
        
        return redirect(url_for("reset_password_form"))

    return render_template("verify_otp.html")
    
# -------- Reset Password After OTP Verification
@app.route("/reset-password-new", methods=["GET", "POST"])
def reset_password_form():

    # Only users who have successfully verified their OTP can continue.
    if not session.get("password_reset_verified"):
        flash("Please verify your OTP first.", "warning")
        return redirect(url_for("forgot_password"))

    user_id = session.get("password_reset_user_id")

    if not user_id:
        return redirect(url_for("forgot_password"))

    if request.method == "POST":

        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Check whether both passwords match.
        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("reset_password_form"))

        # Basic password length validation.
        if len(new_password) < 8:
            flash("Password must contain at least 8 characters.", "danger")
            return redirect(url_for("reset_password_form"))

        # Hash the new password before saving it.
        password_hash = generate_password_hash(new_password)

        with sqlite3.connect(AUTH_DB_PATH) as connection:

            connection.execute(
                """
                UPDATE users
                SET password_hash = ?
                WHERE user_id = ?
                """,
                (password_hash, user_id)
            )

            connection.commit()

        # Clear password-reset session data.
        session.pop("password_reset_user_id", None)
        session.pop("password_reset_verified", None)

        flash("Your password has been reset successfully. Please log in.", "success")

        return redirect(url_for("login"))

    return render_template("reset_password.html")


# -------- Reset Password
@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):

    # Hash the token received from the reset link.
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    with sqlite3.connect(AUTH_DB_PATH) as connection:
        connection.row_factory = sqlite3.Row

        reset_record = connection.execute(
            """
            SELECT token_id, user_id, expires_at
            FROM password_reset_tokens
            WHERE token_hash = ? AND used = 0
            """,
            (token_hash,)
        ).fetchone()

        # Reject invalid or already-used tokens.
        if not reset_record:
            flash("Invalid or already-used reset link.", "error")
            return redirect(url_for("login"))

        # Check whether the token has expired.
        expires_at = datetime.fromisoformat(reset_record["expires_at"])

        if datetime.now(timezone.utc) >= expires_at:
            flash("This reset link has expired. Request a new one.", "error")
            return redirect(url_for("forgot_password"))

        if request.method == "POST":

            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            if len(new_password) < 8:
                flash("Password must contain at least 8 characters.", "error")

            elif new_password != confirm_password:
                flash("Passwords do not match.", "error")

            else:
                password_hash = generate_password_hash(new_password)

                connection.execute(
                    """
                    UPDATE users
                    SET password_hash = ?
                    WHERE user_id = ?
                    """,
                    (password_hash, reset_record["user_id"])
                )

                # Make the reset token unusable.
                connection.execute(
                    """
                    UPDATE password_reset_tokens
                    SET used = 1
                    WHERE user_id = ?
                    """,
                    (reset_record["user_id"],)
                )

                connection.commit()

                flash("Your password has been reset. Please log in.", "success")
                return redirect(url_for("login"))

    return render_template("reset_password.html")
@app.route("/logout", methods=["POST"])
def logout():
    # Remove the logged-in user's session data.
    session.clear()
    return redirect(url_for("login"))


# -------- Generate and Store Password Reset OTP
def generate_password_reset_otp(user_id):

    # Generate a random six-digit OTP.
    otp = f"{secrets.randbelow(1_000_000):06d}"

    # Hash the OTP before storing it.
    otp_hash = hashlib.sha256(otp.encode()).hexdigest()

    # Set OTP expiration to 5 minutes.
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    with sqlite3.connect(AUTH_DB_PATH) as connection:

        # Invalidate any previous unused OTPs for this user.
        connection.execute("""
            UPDATE password_reset_otps
            SET used = 1
            WHERE user_id = ? AND used = 0
        """, (user_id,))

        # Store the new OTP hash.
        connection.execute("""
            INSERT INTO password_reset_otps
            (user_id, otp_hash, expires_at, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            user_id,
            otp_hash,
            expires_at.isoformat(),
            datetime.now(timezone.utc).isoformat()
        ))

        connection.commit()

    # Return the original OTP so we can email it.
    return otp
 
initialize_password_reset_table()

initialize_password_reset_otp_table()
# -------- Temporary Gmail test
if __name__ == "__main__":

  

    # Start Flask after the email test.
    app.run(debug=True)