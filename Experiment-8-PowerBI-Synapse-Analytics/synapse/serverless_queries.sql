-- ============================================================================
-- Experiment 8: Visualize real-time data from Azure Synapse Analytics
-- in Power BI
-- Course: Cloud Analytics (25MCAR0141), Course Outcome: CO3
--
-- Run Queries 1-3 and 5-6 on the Synapse serverless SQL (Built-in)
-- endpoint:  <synapse-workspace>-ondemand.sql.azuresynapse.net
-- Run Query 4 on the Dedicated SQL Pool endpoint:
--              <synapse-workspace>.sql.azuresynapse.net
-- Replace <synapse-workspace> with the actual Synapse workspace name.
-- No credentials are stored in this file -- sign in interactively in
-- Synapse Studio / Power BI Desktop.
--
-- Sources:
--   (a) Experiment 6 cleaned student data (Parquet):
--       calablake141 / output / student_performance_cleaned
--   (b) Dedicated SQL Pool table student_performance (Experiment 2
--       COPY INTO pattern)
--   (c) Experiment 3 passenger data (CSV):
--       caljainstorage1 / raw / Adithya_tej.csv
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Query 1 -- Preview the Experiment 6 cleaned Parquet data (serverless)
-- Confirm the cleaned columns (average_score, performance_band, result)
-- are present before aggregating.
-- ----------------------------------------------------------------------------
SELECT TOP 100 *
FROM OPENROWSET(
    BULK 'https://calablake141.dfs.core.windows.net/output/student_performance_cleaned/*.parquet',
    FORMAT = 'PARQUET'
) AS [cleaned];

-- ----------------------------------------------------------------------------
-- Query 2 -- Average score by performance band (serverless)
-- Feeds the Power BI performance band distribution and average score visuals.
-- ----------------------------------------------------------------------------
SELECT
    performance_band,
    COUNT(*) AS student_count,
    AVG(average_score) AS avg_score
FROM OPENROWSET(
    BULK 'https://calablake141.dfs.core.windows.net/output/student_performance_cleaned/*.parquet',
    FORMAT = 'PARQUET'
) AS [cleaned]
GROUP BY performance_band
ORDER BY avg_score DESC;

-- ----------------------------------------------------------------------------
-- Query 3 -- Pass / fail counts (serverless)
-- Feeds the Power BI pass-rate KPI card.
-- ----------------------------------------------------------------------------
SELECT
    result,
    COUNT(*) AS student_count
FROM OPENROWSET(
    BULK 'https://calablake141.dfs.core.windows.net/output/student_performance_cleaned/*.parquet',
    FORMAT = 'PARQUET'
) AS [cleaned]
GROUP BY result;

-- ----------------------------------------------------------------------------
-- Query 4 -- Dedicated SQL Pool variant (dedicated endpoint only)
-- Same aggregation as Query 2, against the student_performance table
-- loaded into the pool (Experiment 2 COPY INTO pattern). Plain T-SQL --
-- no OPENROWSET, because the data already lives in the pool.
-- Run this on <synapse-workspace>.sql.azuresynapse.net, not on the
-- serverless endpoint.
-- ----------------------------------------------------------------------------
SELECT
    performance_band,
    COUNT(*) AS student_count,
    AVG(average_score) AS avg_score
FROM dbo.student_performance
GROUP BY performance_band
ORDER BY avg_score DESC;

-- ----------------------------------------------------------------------------
-- Query 4b -- Dedicated SQL Pool variant, pass / fail counts
-- Same aggregation as Query 3, against the loaded table.
-- ----------------------------------------------------------------------------
SELECT
    result,
    COUNT(*) AS student_count
FROM dbo.student_performance
GROUP BY result;

-- ----------------------------------------------------------------------------
-- Query 5 -- Second source: preview the Experiment 3 passenger CSV
-- (serverless). Reuses the Experiment 3 OPENROWSET pattern over
-- caljainstorage1 / raw / Adithya_tej.csv (Titanic-style data).
-- ----------------------------------------------------------------------------
SELECT TOP 100 *
FROM OPENROWSET(
    BULK 'https://caljainstorage1.dfs.core.windows.net/raw/Adithya_tej.csv',
    FORMAT = 'CSV',
    PARSER_VERSION = '2.0',
    HEADER_ROW = TRUE
) AS [passengers];

-- ----------------------------------------------------------------------------
-- Query 6 -- Second source: survival rate by passenger class (serverless)
-- Verify the column names against the header row of Adithya_tej.csv
-- before running, and adjust the WITH clause if they differ.
-- ----------------------------------------------------------------------------
SELECT
    Pclass,
    COUNT(*) AS passenger_count,
    AVG(CAST(Survived AS FLOAT)) AS survival_rate
FROM OPENROWSET(
    BULK 'https://caljainstorage1.dfs.core.windows.net/raw/Adithya_tej.csv',
    FORMAT = 'CSV',
    PARSER_VERSION = '2.0',
    HEADER_ROW = TRUE
)
WITH (
    Survived INT,
    Pclass INT
) AS [passengers]
GROUP BY Pclass
ORDER BY Pclass;
