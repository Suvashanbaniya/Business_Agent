import sqlite3

conn = sqlite3.connect("customer.db")

with open("customer_support.sql", "r", encoding="utf-8") as file:
    sql_script = file.read()

conn.executescript(sql_script)

conn.commit()
conn.close()

print("Database imported successfully!")