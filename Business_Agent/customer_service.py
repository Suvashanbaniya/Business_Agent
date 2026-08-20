import sqlite3


DATABASE = "customer.db"


def get_customer_by_email(email):

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM customers
        WHERE email = ?
        """,
        (email,)
    )

    customer = cursor.fetchone()

    conn.close()

    return customer