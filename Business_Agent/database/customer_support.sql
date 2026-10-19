
PRAGMA foreign_keys = ON;

-- =========================
-- 1. CUSTOMERS
-- =========================

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    join_date DATE
);

-- =========================
-- 2. PRODUCTS
-- =========================

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    category TEXT,
    price REAL NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    warranty_months INTEGER DEFAULT 0
);

-- =========================
-- 3. ORDERS
-- =========================

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    order_date DATE,
    status TEXT NOT NULL,
    total_amount REAL NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- =========================
-- 4. ORDER ITEMS
-- =========================

CREATE TABLE order_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- =========================
-- 5. SUPPORT TICKETS
-- =========================

CREATE TABLE support_tickets (
    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    issue_title TEXT NOT NULL,
    issue_description TEXT,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- =========================
-- SAMPLE CUSTOMERS
-- =========================

INSERT INTO customers (full_name, email, phone, join_date)
VALUES
('John Smith', 'john@gmail.com', '980000001', '2025-01-15'),
('Sarah Johnson', 'sarah@gmail.com', '980000002', '2025-02-10'),
('David Lee', 'suvashanb@gmail.com', '980000003', '2025-03-05');

-- =========================
-- SAMPLE PRODUCTS
-- =========================

INSERT INTO products
    (product_name, category, price, stock_quantity, warranty_months)
VALUES
('Smartphone X1', 'Electronics', 799.99, 45, 12),
('Laptop Pro 15', 'Electronics', 1299.99, 20, 24),
('Wireless Headphones', 'Accessories', 149.99, 100, 12),
('Gaming Mouse', 'Accessories', 59.99, 75, 12);

-- =========================
-- SAMPLE ORDERS
-- =========================

INSERT INTO orders (customer_id, order_date, status, total_amount)
VALUES
(1, '2026-01-10', 'Delivered', 949.98),
(2, '2026-02-12', 'Processing', 1299.99),
(3, '2026-03-01', 'Shipped', 149.99);

-- =========================
-- SAMPLE ORDER ITEMS
-- =========================

INSERT INTO order_items (order_id, product_id, quantity)
VALUES
(1, 1, 1),
(1, 4, 1),
(2, 2, 1),
(3, 3, 1);

-- =========================
-- SAMPLE SUPPORT TICKETS
-- =========================

INSERT INTO support_tickets
    (customer_id, issue_title, issue_description, status)
VALUES
(1, 'Refund Request', 'Customer wants refund for damaged item', 'Open'),
(2, 'Late Delivery', 'Package delayed more than expected', 'In Progress');
