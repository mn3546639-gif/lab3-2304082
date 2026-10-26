USE company;

-- Insert departments before assigning their managers.
INSERT INTO DEPARTMENT
    (Dnumber, Dname, mgr_ssn, mgr_start_date)
VALUES
    (1, 'IT', NULL, NULL),
    (2, 'Finance', NULL, NULL),
    (3, 'Engineering', NULL, NULL);
    -- Add employees to existing departments.
INSERT INTO EMPLOYEE
    (ssn, fname, lname, bdate, address, gender, salary, Dno)
VALUES
    ('123456789', 'Ahmed', 'Ali', '1990-05-15',
     'Alexandria', 'M', 15000.00, 1),

    ('234567890', 'Mona', 'Hassan', '1992-08-20',
     'Cairo', 'F', 14000.00, 2),

    ('345678901', 'Omar', 'Mahmoud', '1988-03-10',
     'Damanhour', 'M', 16000.00, 3);
     -- Assign an existing employee as each department's manager.
UPDATE DEPARTMENT
SET mgr_ssn = '123456789',
    mgr_start_date = '2025-01-01'
WHERE Dnumber = 1;

UPDATE DEPARTMENT
SET mgr_ssn = '234567890',
    mgr_start_date = '2025-02-01'
WHERE Dnumber = 2;

UPDATE DEPARTMENT
SET mgr_ssn = '345678901',
    mgr_start_date = '2025-03-01'
WHERE Dnumber = 3;
-- Add projects belonging to existing departments.
INSERT INTO PROJECT
    (Pnumber, Pname, Plocation, Dno)
VALUES
    (101, 'Network Upgrade', 'Alexandria', 1),
    (102, 'Budget System', 'Cairo', 2),
    (103, 'Plant Expansion', 'Damanhour', 3);