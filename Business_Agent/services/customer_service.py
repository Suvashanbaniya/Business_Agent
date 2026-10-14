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

def get_customer_by_orders(customer_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute(
    """
    SELECT * 
    FROM orders
    WHERE customer_id = ?
    
    
    """,
    (customer_id,)
    )
    
    orders = cursor.fetchall()
    conn.close()
    
    return orders 


def get_customer_by_tickets(customer_id):
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute(
    """
    SELECT * 
    FROM support_tickets
    WHERE customer_id = ?

    """,
    (customer_id,)
    )
    tickets = cursor.fetchall()
    conn.close ()
    return tickets


def get_customer_context(email):
    
    customer = get_customer_by_email(email)
    
    if not customer:
        return None
    
    customer_id = customer[0]
    orders = get_customer_by_orders(customer_id)
    
    tickets = get_customer_by_tickets(customer_id)
    
    context = {
        "customer":customer,
        "orders":orders,
        "tickets":tickets
    }
    
    return context 