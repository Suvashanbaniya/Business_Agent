
import sqlite3
from pathlib import Path

#-------- Locate the project and database
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "database" / "customer.db"
SQL_PATH = BASE_DIR / "database" / "customer_support.sql"

conn = sqlite3.connect(DATABASE_PATH)

try:
    with open(SQL_PATH, "r", encoding="utf-8") as file:
        sql_script = file.read()

    conn.executescript(sql_script)
    conn.commit()

    print("Database imported successfully!")

except sqlite3.Error as error:
    conn.rollback()
    print("Database import failed:", error)

finally:
    conn.close()
