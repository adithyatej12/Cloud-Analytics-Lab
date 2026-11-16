-- Experiment 7: Connect Power BI to Azure SQL and create a dashboard
-- with real-time insights.
-- Course: Cloud Analytics (25MCAR0141), Course Outcome CO3.
--
-- Run this script in the Azure SQL Database query editor against
-- database calab-sqldb-141 (server <server-name>, resource group
-- 25MCAR0141, region centralindia).
--
-- No credentials are stored in this file. Sign in to the query editor
-- with the SQL admin login created in the portal (<username> /
-- <password> placeholders only - never write real credentials here).

CREATE TABLE student_performance (
    student_id INT PRIMARY KEY,
    student_name NVARCHAR(100) NOT NULL,
    math_score INT NOT NULL,
    english_score INT NOT NULL,
    science_score INT NOT NULL
);
GO

INSERT INTO student_performance (student_id, student_name, math_score, english_score, science_score) VALUES
    (1,  'Aarav Sharma',  78, 85, 82),
    (2,  'Priya Nair',    92, 88, 90),
    (3,  'Rohan Verma',   45, 52, 38),
    (4,  'Sneha Iyer',    67, 74, 71),
    (5,  'Vikram Rao',    88, 81, 85),
    (6,  'Ananya Gupta',  95, 91, 93),
    (7,  'Karthik Menon', 34, 41, 29),
    (8,  'Divya Reddy',   73, 69, 76),
    (9,  'Arjun Pillai',  58, 63, 55),
    (10, 'Meera Joshi',   81, 77, 84),
    (11, 'Nikhil Kumar',  49, 44, 52),
    (12, 'Kavya Singh',   90, 86, 89);
GO

-- Verify the load: expect 12 rows.
SELECT COUNT(*) AS row_count FROM student_performance;
GO
