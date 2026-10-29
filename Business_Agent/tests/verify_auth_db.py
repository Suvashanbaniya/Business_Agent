import sqlite3
from pathlib import Path
from werkzeug.security import check_password_hash

DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "database"
    / "auth.db"
)

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

# Fetch account details without exposing password hashes.
cursor.execute("""
    SELECT login_id, role, customer_id
    FROM users
""")

users = cursor.fetchall()

print("Accounts found:")
for user in users:
    print(user)

# Test whether the password for customer 1001 is correct.
cursor.execute("""
    SELECT password_hash
    FROM users
    WHERE login_id = ?
""", ("1001",))

result = cursor.fetchone()

if result:
    password_is_valid = check_password_hash(
        result[0], "Customer@123"
    )
    print("Customer password valid:", password_is_valid)
else:
    print("Customer 1001 was not found.")

connection.close()