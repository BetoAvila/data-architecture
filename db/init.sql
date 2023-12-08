CREATE DATABASE db;

USE db;

CREATE USER 'db_user' @'localhost' IDENTIFIED BY 'password';

GRANT
    ALL PRIVILEGES ON db.* TO 'db_user' @'localhost' IDENTIFIED BY 'password';

-- Creating jobs table

CREATE TABLE
    jobs(
        job_id INT NOT NULL AUTO_INCREMENT,
        job_title VARCHAR(100) NOT NULL,
        PRIMARY KEY (job_id)
    );

-- Creating departments table

CREATE TABLE
    departments(
        department_id INT NOT NULL AUTO_INCREMENT,
        department_title VARCHAR(100) NOT NULL,
        PRIMARY KEY (department_id)
    );

-- Creating employees table

CREATE TABLE
    employees(
        employee_id INT NOT NULL AUTO_INCREMENT,
        employee_name VARCHAR(200) NOT NULL,
        hiring_date DATETIME NOT NULL,
        department_id INT NOT NULL,
        job_id INT NOT NULL,
        PRIMARY KEY (employee_id)
    );