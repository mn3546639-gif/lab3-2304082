DROP DATABASE IF EXISTS company;
CREATE DATABASE company;
USE company;

CREATE TABLE DEPARTMENT (
    Dnumber INT PRIMARY KEY,
    Dname VARCHAR(50) NOT NULL,
    mgr_ssn CHAR(9),
    mgr_start_date DATE
);

CREATE TABLE EMPLOYEE (
    ssn CHAR(9) PRIMARY KEY,
    fname VARCHAR(50) NOT NULL,
    lname VARCHAR(50) NOT NULL,
    bdate DATE,
    address VARCHAR(150),
    gender CHAR(1),
    salary DECIMAL(10,2),
    Dno INT,

    FOREIGN KEY (Dno)
        REFERENCES DEPARTMENT(Dnumber)
);

-- Add this foreign key after EMPLOYEE exists.
ALTER TABLE DEPARTMENT
ADD CONSTRAINT fk_department_manager
FOREIGN KEY (mgr_ssn)
REFERENCES EMPLOYEE(ssn);

CREATE TABLE PROJECT (
    Pnumber INT PRIMARY KEY,
    Pname VARCHAR(50) NOT NULL,
    Plocation VARCHAR(100),
    Dno INT,

    FOREIGN KEY (Dno)
        REFERENCES DEPARTMENT(Dnumber)
);