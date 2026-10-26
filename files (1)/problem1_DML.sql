-- Problem 1: COMPANY database (DML = the data)
USE company;

-- EMPLOYEE and DEPARTMENT point to each other and both columns are NOT NULL,
-- so whichever table we fill first breaks the rule. We switch the foreign key check
-- off, insert everything, then switch it back on (see Q1.3).
SET FOREIGN_KEY_CHECKS = 0;

INSERT INTO EMPLOYEE (ssn, fname, lname, bdate, address, gender, salary, Dno) VALUES
(111111111, 'Ahmed', 'Hassan',  '1990-05-12', 'Alexandria', 'M', 8500.00, 1),
(222222222, 'Sara',  'Mahmoud', '1992-08-20', 'Cairo',      'F', 9200.00, 2),
(333333333, 'Omar',  'Khaled',  '1988-01-03', 'Giza',       'M', 7800.00, 3),
(444444444, 'Mona',  'Ali',     '1995-11-25', 'Alexandria', 'F', 6500.00, 1);

INSERT INTO DEPARTMENT (Dnumber, Dname, mgr_ssn, mgr_start_date) VALUES
(1, 'Engineering', 111111111, '2020-01-01'),
(2, 'Finance',     222222222, '2021-03-15'),
(3, 'HR',          333333333, '2019-07-01');

INSERT INTO PROJECT (Pnumber, Pname, Plocation, Dno) VALUES
(1, 'Website Redesign', 'Alexandria', 1),
(2, 'Budget System',    'Cairo',      2),
(3, 'Recruitment App',  'Giza',       3),
(4, 'Mobile App',       'Alexandria', 1);

SET FOREIGN_KEY_CHECKS = 1;
