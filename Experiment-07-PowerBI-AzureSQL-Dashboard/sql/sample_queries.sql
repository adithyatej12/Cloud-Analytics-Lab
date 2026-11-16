-- Experiment 7: Connect Power BI to Azure SQL and create a dashboard
-- with real-time insights.
-- Course: Cloud Analytics (25MCAR0141), Course Outcome CO3.
--
-- Sample queries against the student_performance table in database
-- calab-sqldb-142 (server calab-sql-142, resource group 25MCAR0142).
-- Run these in the query editor after loading the table with
-- create_student_performance.sql, and record the observed values.

-- 1. Average score by subject (one row, one column per subject).
SELECT
    AVG(CAST(math_score AS FLOAT)) AS avg_math,
    AVG(CAST(english_score AS FLOAT)) AS avg_english,
    AVG(CAST(science_score AS FLOAT)) AS avg_science
FROM student_performance;
GO

-- 2. Average score by subject (one row per subject - easier to chart).
SELECT 'Math' AS subject, AVG(CAST(math_score AS FLOAT)) AS avg_score
FROM student_performance
UNION ALL
SELECT 'English', AVG(CAST(english_score AS FLOAT))
FROM student_performance
UNION ALL
SELECT 'Science', AVG(CAST(science_score AS FLOAT))
FROM student_performance;
GO

-- 3. Pass rate. A student passes when their average across the three
--    subjects is >= 40.
SELECT
    COUNT(*) AS total_students,
    SUM(CASE WHEN (math_score + english_score + science_score) / 3.0 >= 40 THEN 1 ELSE 0 END) AS passed_students,
    SUM(CASE WHEN (math_score + english_score + science_score) / 3.0 >= 40 THEN 0 ELSE 1 END) AS failed_students,
    100.0 * SUM(CASE WHEN (math_score + english_score + science_score) / 3.0 >= 40 THEN 1 ELSE 0 END) / COUNT(*) AS pass_rate_pct
FROM student_performance;
GO

-- 4. Top 5 students by average score.
SELECT TOP 5
    student_id,
    student_name,
    math_score,
    english_score,
    science_score,
    (math_score + english_score + science_score) / 3.0 AS average_score
FROM student_performance
ORDER BY average_score DESC;
GO

-- 5. All students with average score and pass/fail result.
SELECT
    student_id,
    student_name,
    (math_score + english_score + science_score) / 3.0 AS average_score,
    CASE WHEN (math_score + english_score + science_score) / 3.0 >= 40 THEN 'Pass' ELSE 'Fail' END AS result
FROM student_performance
ORDER BY average_score DESC;
GO
