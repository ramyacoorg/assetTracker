 DATABASE DUMP : AssetTracker



DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS asset_contracts;
DROP TABLE IF EXISTS asset_requests;
DROP TABLE IF EXISTS asset_issues;
DROP TABLE IF EXISTS asset_assignments;
DROP TABLE IF EXISTS assets;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

 1. Departments
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


 2. Employees

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    employee_code VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    department_id INT,
    joining_date DATE,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


 3. Users (Role-Based Login)

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    employee_id INT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(30) NOT NULL, 
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


4. Assets

CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    asset_code VARCHAR(50) UNIQUE NOT NULL,
    asset_name VARCHAR(100) NOT NULL,
    asset_category VARCHAR(50), 
    asset_status VARCHAR(30) DEFAULT 'AVAILABLE',
    purchase_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

 5. Asset Assignments & Returns

CREATE TABLE asset_assignments (
    id SERIAL PRIMARY KEY,
    asset_id INT NOT NULL,
    employee_id INT NOT NULL,
    assigned_date DATE NOT NULL,
    return_date DATE,
    status VARCHAR(30) DEFAULT 'ASSIGNED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


 6. Asset Issues & Feedback

CREATE TABLE asset_issues (
    id SERIAL PRIMARY KEY,
    asset_id INT NOT NULL,
    employee_id INT NOT NULL,
    issue_description TEXT NOT NULL,
    issue_status VARCHAR(30) DEFAULT 'OPEN',
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


 7. Asset Requests & Approval

CREATE TABLE asset_requests (
    id SERIAL PRIMARY KEY,
    employee_id INT NOT NULL,
    asset_category VARCHAR(50),
    reason TEXT,
    request_status VARCHAR(30) DEFAULT 'PENDING', 
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP
);

 8. Asset Contracts / Expiry Tracking

CREATE TABLE asset_contracts (
    id SERIAL PRIMARY KEY,
    asset_id INT NOT NULL,
    contract_type VARCHAR(50), 
    start_date DATE,
    expiry_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

 9. Notifications & Alerts

CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INT,
    notification_type VARCHAR(50),
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


DUMMY DATA INSERTION

 Departments
INSERT INTO departments (department_name) VALUES
('HR'), ('IT'), ('Finance'), ('Operations');

 Employees
INSERT INTO employees (employee_code, full_name, email, department_id, joining_date)
VALUES
('EMP001', 'Anita Sharma', 'anita@company.com', 1, '2021-06-10'),
('EMP002', 'Rohit Kumar', 'rohit@company.com', 2, '2022-01-15');

 Users
INSERT INTO users (employee_id, username, password_hash, role)
VALUES
(1, 'admin_anita', 'hashed_admin_pwd', 'ADMIN'),
(2, 'emp_rohit', 'hashed_emp_pwd', 'EMPLOYEE');

Assets
INSERT INTO assets (asset_code, asset_name, asset_category, purchase_date)
VALUES
('AST001', 'Dell Laptop', 'Laptop', '2022-03-01'),
('AST002', 'MS Office License', 'Software', '2023-01-10');

 Asset Assignments
INSERT INTO asset_assignments (asset_id, employee_id, assigned_date)
VALUES
(1, 2, '2022-03-05');

 Asset Issues
INSERT INTO asset_issues (asset_id, employee_id, issue_description)
VALUES
(1, 2, 'Laptop battery draining quickly');

Asset Requests
INSERT INTO asset_requests (employee_id, asset_category, reason)
VALUES
(2, 'Mobile', 'Required for official communication');

 Asset Contracts
INSERT INTO asset_contracts (asset_id, contract_type, start_date, expiry_date)
VALUES
(2, 'LICENSE', '2023-01-10', '2024-01-10');

 Notifications
INSERT INTO notifications (user_id, notification_type, message)
VALUES
(1, 'ASSET_REQUEST', 'New asset request pending approval');
