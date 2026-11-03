import sqlite3
from pathlib import Path
from contextlib import closing

# Path to the customer database
DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "database"
    / "customer.db"
)

def add_ticket_message(ticket_id, sender_id, sender_role, message):

    # Check whether the sender role is valid
    if sender_role not in ("customer", "admin"):
        raise ValueError("Invalid sender role.")

    # Prevent empty messages
    message = message.strip()

    if not message:
        raise ValueError("Message cannot be empty.")

    with closing(sqlite3.connect(DB_PATH)) as conn:

        # Check whether the ticket exists
        cursor = conn.execute(
            """
            SELECT ticket_id
            FROM support_tickets
            WHERE ticket_id = ?
            """,
            (ticket_id,)
        )

        if cursor.fetchone() is None:
            raise ValueError("Ticket not found.")

        # Save the message
        cursor = conn.execute(
            """
            INSERT INTO ticket_messages
            (ticket_id, sender_id, sender_role, message)
            VALUES (?, ?, ?, ?)
            """,
            (ticket_id, sender_id, sender_role, message)
        )

        message_id = cursor.lastrowid

        conn.commit()

        return message_id
    

def get_ticket_messages(ticket_id):

    with closing(sqlite3.connect(DB_PATH)) as conn:

        # Return database rows as dictionaries
        conn.row_factory = sqlite3.Row

        cursor = conn.execute(
            """
            SELECT
                message_id,
                ticket_id,
                sender_id,
                sender_role,
                message,
                created_at
            FROM ticket_messages
            WHERE ticket_id = ?
            ORDER BY message_id ASC
            """,
            (ticket_id,)
        )

        # Convert each database row into a dictionary
        messages = [dict(row) for row in cursor.fetchall()]

        return messages