-- Create and use the database
CREATE DATABASE IF NOT EXISTS Supermarket;
USE Supermarket;

-- Create Customers table
CREATE TABLE IF NOT EXISTS CUSTOMERS (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    membership BOOLEAN DEFAULT FALSE,
    password VARCHAR(255) NOT NULL DEFAULT 'password123'
) ENGINE=InnoDB;

-- Create Branches table
CREATE TABLE IF NOT EXISTS BRANCHES (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(255) NOT NULL,
    size INT DEFAULT 0,
    total_stock INT DEFAULT 0
) ENGINE=InnoDB;

-- Create Employees table
CREATE TABLE IF NOT EXISTS EMPLOYEES (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    dateOfEmployment DATE,
    dateOfEndOfEmployment DATE DEFAULT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    role VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL DEFAULT 'password123'
) ENGINE=InnoDB;

-- Create Products table
CREATE TABLE IF NOT EXISTS PRODUCTS (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    stock INT DEFAULT 0,
    sellPrice DECIMAL(10, 2) NOT NULL,
    cost DECIMAL(10, 2) NOT NULL,
    category_id VARCHAR(10) NOT NULL,
    category VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

-- Create Transactions table
CREATE TABLE IF NOT EXISTS TRANSACTIONS (
    id INT AUTO_INCREMENT PRIMARY KEY,
    branch_id INT,
    customer_id INT,
    total_amount DECIMAL(10, 2) NOT NULL,
    dateOfTransaction DATE NOT NULL,
    timeOfTransaction TIME NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (branch_id) REFERENCES BRANCHES(id) ON DELETE SET NULL,
    FOREIGN KEY (customer_id) REFERENCES CUSTOMERS(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Create Transaction_Details table
CREATE TABLE IF NOT EXISTS TRANSACTION_DETAILS (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES TRANSACTIONS(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(id) ON DELETE SET NULL
) ENGINE=InnoDB;