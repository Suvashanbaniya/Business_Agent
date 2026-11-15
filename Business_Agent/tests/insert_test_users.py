import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

# Find auth.db inside the database folder.
DB_PATH = (
    Path(__file__).resolve().parent
    / "Business_Agent"
    / "database"
    / "auth.db"
)

# Connect to the authentication database.
connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

# Create the users table if it doesn't exist.
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        login_id TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK (role IN ('customer', 'admin')),
        customer_id INTEGER UNIQUE
    )
""")

connection.commit()

print("Users table created or already exists.")

print("Existing tables:", cursor.fetchall())
# Test accounts: login ID, password, role, linked customer ID.
test_users = [
    ("1001", "Customer@123", "customer", 1),
    ("1002", "Customer@456", "customer", 2),
    ("admin01", "Admin@123", "admin", None),
]

try:
    for login_id, password, role, customer_id in test_users:

        # Convert the password into a secure hash before saving.
        password_hash = generate_password_hash(password)

        # Insert the account into the users table.
        cursor.execute(
            """
            INSERT OR IGNORE INTO users
                (login_id, password_hash, role, customer_id)
            VALUES (?, ?, ?, ?)
            """,
            (login_id, password_hash, role, customer_id)
        )

    connection.commit()
    print("Test accounts inserted successfully!")

except sqlite3.Error as error:
    connection.rollback()
    print("Database error:", error)

finally:
    connection.close()