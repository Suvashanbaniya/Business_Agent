
import sqlite3
from pathlib import Path

#-------- Find the existing database
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "database" / "customer.db"

conn = sqlite3.connect(DATABASE_PATH)

try:
    cursor = conn.cursor()

    #-------- Add sample data only if the table is empty
    cursor.execute("SELECT COUNT(*) FROM order_items")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany("""
            INSERT INTO order_items (order_id, product_id, quantity)
            VALUES (?, ?, ?)
        """, [
            (1, 1, 1),
            (1, 4, 1),
            (2, 2, 1),
            (3, 3, 1)
        ])

        conn.commit()
        print("Sample order items inserted.")
    else:
        print(f"Order items already exist: {count}")

    cursor.execute("SELECT COUNT(*) FROM order_items")
    print("Final order item count:", cursor.fetchone()[0])

except sqlite3.Error:
    conn.rollback()
    raise

finally:
    conn.close()
