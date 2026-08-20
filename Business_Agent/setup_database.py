import sqlite3


conn = sqlite3.connect("customer.db")

cursor = conn.cursor()


# Remove existing tables
cursor.execute("DROP TABLE IF EXISTS support_tickets")
cursor.execute("DROP TABLE IF EXISTS order_items")
cursor.execute("DROP TABLE IF EXISTS orders")
cursor.execute("DROP TABLE IF EXISTS products")
cursor.execute("DROP TABLE IF EXISTS customers")


# Customers table
cursor.execute("""
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT,
    email TEXT,
    phone TEXT,
    join_date DATE
)
""")


# Products table
cursor.execute("""
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT,
    category TEXT,
    price REAL,
    stock_quantity INTEGER,
    warranty_months INTEGER
)
""")


# Orders table
cursor.execute("""
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    order_date DATE,
    status TEXT,
    total_amount REAL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
)
""")


# Order items table
cursor.execute("""
CREATE TABLE order_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
)
""")


# Support tickets table
cursor.execute("""
CREATE TABLE support_tickets (
    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    issue_title TEXT,
    issue_description TEXT,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
)
""")


# Insert customers
cursor.executemany("""
INSERT INTO customers
(full_name, email, phone, join_date)
VALUES (?, ?, ?, ?)
""", [
    ("John Smith", "john@gmail.com", "980000001", "2025-01-15"),
    ("Sarah Johnson", "sarah@gmail.com", "980000002", "2025-02-10"),
    ("David Lee", "suvashanb@gmail.com", "980000003", "2025-03-05")
])


# Insert products
cursor.executemany("""
INSERT INTO products
(product_name, category, price, stock_quantity, warranty_months)
VALUES (?, ?, ?, ?, ?)
""", [
    ("Smartphone X1", "Electronics", 799.99, 45, 12),
    ("Laptop Pro 15", "Electronics", 1299.99, 20, 24),
    ("Wireless Headphones", "Accessories", 149.99, 100, 12),
    ("Gaming Mouse", "Accessories", 59.99, 75, 12)
])


# Insert orders
cursor.executemany("""
INSERT INTO orders
(customer_id, order_date, status, total_amount)
VALUES (?, ?, ?, ?)
""", [
    (1, "2026-01-10", "Delivered", 949.98),
    (2, "2026-02-12", "Processing", 1299.99),
    (3, "2026-03-01", "Shipped", 149.99)
])


# Insert support tickets
cursor.executemany("""
INSERT INTO support_tickets
(customer_id, issue_title, issue_description, status)
VALUES (?, ?, ?, ?)
""", [
    (1, "Refund Request",
     "Customer wants refund for damaged item", "Open"),

    (2, "Late Delivery",
     "Package delayed more than expected", "In Progress")
])


conn.commit()

conn.close()


print("Database created successfully.")