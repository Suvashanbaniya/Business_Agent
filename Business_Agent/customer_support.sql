-- Customers
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    join_date DATE
);

-- Products
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10,2),
    stock_quantity INT,
    warranty_months INT
);

-- Orders
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    order_date DATE,
    status VARCHAR(50),
    total_amount DECIMAL(10,2)
);

-- Order Items
CREATE TABLE order_items (
    item_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id),
    product_id INT REFERENCES products(product_id),
    quantity INT
);

-- Support Tickets
CREATE TABLE support_tickets (
    ticket_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    issue_title VARCHAR(200),
    issue_description TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO customers(full_name,email,phone,join_date)
VALUES
('John Smith','john@gmail.com','980000001','2025-01-15'),
('Sarah Johnson','sarah@gmail.com','980000002','2025-02-10'),
('David Lee','suvashanb@gmail.com','980000003','2025-03-05');

INSERT INTO products(product_name,category,price,stock_quantity,warranty_months)
VALUES
('Smartphone X1','Electronics',799.99,45,12),
('Laptop Pro 15','Electronics',1299.99,20,24),
('Wireless Headphones','Accessories',149.99,100,12),
('Gaming Mouse','Accessories',59.99,75,12);

INSERT INTO orders(customer_id,order_date,status,total_amount)
VALUES
(1,'2026-01-10','Delivered',949.98),
(2,'2026-02-12','Processing',1299.99),
(3,'2026-03-01','Shipped',149.99);

INSERT INTO support_tickets(customer_id,issue_title,issue_description,status)
VALUES
(1,'Refund Request','Customer wants refund for damaged item','Open'),
(2,'Late Delivery','Package delayed more than expected','In Progress');