-- Problem 1: COMPANY database (DDL)

-- Delete the old database (if any) and build a fresh one, so the script can be re-run any time
DROP DATABASE IF EXISTS company;
CREATE DATABASE company;
USE company;

-- EMPLOYEE is created first, WITHOUT the foreign key Dno
-- (DEPARTMENT does not exist yet; the foreign key is added later with ALTER TABLE)
CREATE TABLE EMPLOYEE (
    ssn      INT           NOT NULL,
    fname    VARCHAR(30)   NOT NULL,
    lname    VARCHAR(30)   NOT NULL,
    bdate    DATE,
    address  VARCHAR(100),
    gender   CHAR(1),
    salary   DECIMAL(10,2),
    Dno      INT           NOT NULL,
    PRIMARY KEY (ssn)
);

-- DEPARTMENT points to EMPLOYEE (the manager), so EMPLOYEE must exist before it
CREATE TABLE DEPARTMENT (
    Dnumber        INT          NOT NULL,
    Dname          VARCHAR(50)  NOT NULL,
    mgr_ssn        INT          NOT NULL,
    mgr_start_date DATE,
    PRIMARY KEY (Dnumber),
    FOREIGN KEY (mgr_ssn) REFERENCES EMPLOYEE(ssn)
);

-- PROJECT points to DEPARTMENT, so DEPARTMENT must exist before it
CREATE TABLE PROJECT (
    Pnumber   INT          NOT NULL,
    Pname     VARCHAR(50)  NOT NULL,
    Plocation VARCHAR(50),
    Dno       INT          NOT NULL,
    PRIMARY KEY (Pnumber),
    FOREIGN KEY (Dno) REFERENCES DEPARTMENT(Dnumber)
);

-- Now DEPARTMENT exists, so we can add the last foreign key: EMPLOYEE.Dno -> DEPARTMENT.Dnumber
ALTER TABLE EMPLOYEE ADD FOREIGN KEY (Dno)
    REFERENCES DEPARTMENT(Dnumber);
