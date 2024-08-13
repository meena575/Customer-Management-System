-- Use the correct database
USE client_management;

-- create the services table

CREATE TABLE services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    service_name VARCHAR(255),
    description VARCHAR(255),
    price DECIMAL(10, 2),
    status VARCHAR(50)
);
SELECT * FROM services;

-- create the users table

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(255),
    role ENUM('admin', 'client', 'user') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    phone_number VARCHAR(20),
    address VARCHAR(255)
);

-- create the invoices table
CREATE TABLE invoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    invoice_date DATE,
    due_date DATE,
    total_amount DECIMAL(10, 2),
    status VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
SELECT * FROM users;

-- create the client_services table
CREATE TABLE client_services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    service_id INT,
    assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);

-- create the subscriptions_table
CREATE TABLE subscriptions_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    service_id INT,
    subscription_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiration_date TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL 3 MONTH),
    status ENUM('requested', 'active', 'cancelled') DEFAULT 'requested',
    payment_method ENUM('cash', 'credit_card', 'debit_card', 'paypal', 'bank_transfer') DEFAULT 'cash',
    amount_paid DECIMAL(10, 2) DEFAULT 0.00,
    amount_unpaid DECIMAL(10, 2) DEFAULT 0.00,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);
select * from invoices where status="Paid";

update invoices 
set status='Paid'
where status='paid';
