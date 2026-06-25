import sqlite3

conn = sqlite3.connect("customer.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    full_name TEXT,
    email TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully!")