# Experiment 8: Visualize real-time data from Azure Synapse Analytics in Power BI

**Course:** Cloud Analytics (25MCAR0141)
**Course Outcome:** CO3
**Target document:** CA_Exp08_PowerBI_Synapse.pdf (also in this folder)

## Aim

To visualize data stored in Azure Synapse Analytics in Power BI by querying lake data through Synapse serverless SQL, connecting Power BI Desktop to Synapse with DirectQuery, and building live visuals that reflect the underlying data as it changes.

## Objectives

- Query the cleaned student data from Experiment 6 through Synapse serverless SQL using OPENROWSET over Parquet files in ADLS Gen2.
- Compare the serverless SQL endpoint with the Dedicated SQL Pool endpoint created in Experiment 2.
- Connect Power BI Desktop to Azure Synapse Analytics SQL using DirectQuery for near-real-time visuals.
- Build visuals for performance band distribution, average score, and pass-rate KPI.
- Explain DirectQuery refresh behaviour versus Import mode scheduled refresh.
- Pause or scale down the dedicated SQL pool after the lab to save cost.

## Architecture

```text
ADLS Gen2 (calablake141 / output)
        |  Parquet: student_performance_cleaned (from Experiment 6)
        v
Azure Synapse Analytics (<synapse-workspace>)
        |  Serverless SQL (Built-in endpoint) -- OPENROWSET over the lake
        |  Dedicated SQL Pool -- student_performance table (Experiment 2 pattern)
        v
Power BI Desktop
        |  Get Data -> Azure Synapse Analytics SQL (DirectQuery)
        |  Visuals: performance band distribution, average score, pass-rate KPI
        v
Live report -- each interaction re-queries Synapse

Second source (Experiment 3 pattern):
ADLS Gen2 (caljainstorage1 / raw / Adithya_tej.csv)
        |  OPENROWSET over CSV, via serverless SQL
        v
Azure Synapse Analytics (<synapse-workspace>)
```

Synapse sits between the lake and Power BI: the serverless endpoint queries files in place without loading them anywhere, while the dedicated pool queries tables loaded into the pool. Power BI talks to either endpoint through the same connector — what changes is which endpoint you point it at and whether the data is queried live or imported.

## Architecture & Component Roles

| Component | Resource Name | Role / Description |
|---|---|---|
| Resource Group | 25MCAR0141 | Logical container for all Azure experiment resources |
| Storage Account | calablake141 | ADLS Gen2 hosting output/student_performance_cleaned (Parquet, from Experiment 6) |
| Storage Account | caljainstorage1 | ADLS Gen2 hosting raw/Adithya_tej.csv (Titanic-style passenger data, from Experiment 3) |
| Synapse Workspace | <synapse-workspace> | Analytics workspace unifying serverless SQL and the Dedicated SQL Pool |
| Serverless SQL Pool | Built-in | Queries lake files in place with OPENROWSET; no data loading, pay per query |
| Dedicated SQL Pool | (created in Experiment 2) | Provisioned MPP pool querying loaded tables such as student_performance |
| Power BI Desktop | Local | Builds DirectQuery visuals against the Synapse SQL endpoints |

## Services Used

- Azure Synapse Analytics (Serverless SQL + Dedicated SQL Pool)
- Azure Data Lake Storage Gen2
- Power BI Desktop
- Azure Portal / Synapse Studio

## Procedure

### Step 1 — Open Synapse Studio

Azure Portal → `<synapse-workspace>` → Launch Synapse Studio. Confirm the workspace opens and the Data hub lists the lake storage accounts (`calablake141`, `caljainstorage1`).

### Step 2 — Open a Serverless SQL Script

Develop → + → SQL script → connect to the **Built-in** (serverless) pool. This is the endpoint that queries files directly; nothing needs to be loaded first.

### Step 3 — Preview the Experiment 6 Cleaned Data

Run the preview query from `synapse/serverless_queries.sql` (Query 1) — a `SELECT TOP 100` over the Parquet files in `calablake141/output/student_performance_cleaned`. Confirm the cleaned columns are there (`average_score`, `performance_band`, `result`).

### Step 4 — Average Score by Performance Band

Run Query 2 (average score and student count grouped by `performance_band`). Record the observed value here for each band — the numbers depend on the actual run.

### Step 5 — Pass / Fail Counts

Run Query 3 (student counts grouped by `result`). Record the observed value here for Pass and Fail.

### Step 6 — Dedicated Pool Variant

Switch to the **Dedicated SQL Pool** endpoint and run Query 4, the same band aggregation against the `student_performance` table in the pool. Note the difference: the dedicated pool queries a loaded table with plain T-SQL, while the serverless pool queries the Parquet files in place with OPENROWSET. If the table was not loaded in this session, load it first using the COPY INTO pattern from Experiment 2.

### Step 7 — Second Source: Experiment 3 Passenger Data

Back on the serverless endpoint, run Query 5 — the Experiment 3 pattern, OPENROWSET over `caljainstorage1/raw/Adithya_tej.csv`. Preview the rows first; then run Query 6, the survival-rate-by-class aggregation, adjusting the column names in the WITH clause to match the header row of the file if they differ.

### Step 8 — Verify Results

Compare the serverless results with the dedicated pool results for the same aggregation — they should agree. Record the observed value here for the row counts from each query before moving to Power BI.

### Step 9 — Connect Power BI Desktop to Synapse

Power BI Desktop → Get Data → Azure → Azure Synapse Analytics SQL. Enter the server name for the endpoint you want:

- Serverless endpoint: `<synapse-workspace>-ondemand.sql.azuresynapse.net`
- Dedicated pool endpoint: `<synapse-workspace>.sql.azuresynapse.net`

Sign in with your Azure AD account (no key or connection string is stored in this repo — sign in interactively in Power BI). Choose **DirectQuery** as the data connectivity mode.

### Step 10 — Choose DirectQuery

Select DirectQuery, not Import. DirectQuery means Power BI sends a live query to Synapse every time a visual is rendered or a filter changes, so the report reflects the current data without a refresh step. Import would copy a snapshot into the report file instead.

### Step 11 — Build the Visuals

Build three visuals from the serverless query results:

- **Performance band distribution** — bar or donut chart of student count by `performance_band`.
- **Average score** — bar chart of average score by `performance_band` (or a clustered column combining count and average).
- **Pass-rate KPI** — card visual showing the pass rate (Pass count / total students), with the Pass and Fail counts alongside.

### Step 12 — Test the Live Behaviour

Change a filter or slicer on the report and watch the visual update — with DirectQuery, each interaction issues a fresh query against Synapse. Note the behaviour: DirectQuery = live query on interaction; there is no scheduled refresh to configure. Scheduled refresh only applies to Import mode datasets, where Power BI re-imports a snapshot on a timetable.

### Step 13 — Save the Report

Save the report as `Exp08_PowerBI_Synapse.pbix` (local file — not committed to this folder).

### Step 14 — Pause the Dedicated SQL Pool

After the lab, pause (or scale down) the dedicated SQL pool in Synapse Studio to stop the compute meter — the serverless endpoint needs no pause step because it bills per query, but a running dedicated pool keeps charging. This is the cost-saving step; do not skip it.

## SQL Highlights

Full queries: [`synapse/serverless_queries.sql`](synapse/serverless_queries.sql)

**Average score by performance band (serverless, over the Experiment 6 Parquet output):**

```sql
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
```

**Pass / fail counts (serverless):**

```sql
SELECT
    result,
    COUNT(*) AS student_count
FROM OPENROWSET(
    BULK 'https://calablake141.dfs.core.windows.net/output/student_performance_cleaned/*.parquet',
    FORMAT = 'PARQUET'
) AS [cleaned]
GROUP BY result;
```

**Dedicated pool variant — same aggregation, loaded table, plain T-SQL:**

```sql
SELECT
    performance_band,
    COUNT(*) AS student_count,
    AVG(average_score) AS avg_score
FROM dbo.student_performance
GROUP BY performance_band
ORDER BY avg_score DESC;
```

**Second source — Experiment 3 pattern over the passenger CSV:**

```sql
SELECT TOP 100 *
FROM OPENROWSET(
    BULK 'https://caljainstorage1.dfs.core.windows.net/raw/Adithya_tej.csv',
    FORMAT = 'CSV',
    PARSER_VERSION = '2.0',
    HEADER_ROW = TRUE
) AS [passengers];
```

The serverless queries read the lake files in place — no COPY INTO, no loading step. That is the point of the Built-in endpoint: query first, load only if you need the dedicated pool's performance for repeated heavy queries. The dedicated pool variant exists so the two endpoints can be compared on the same question.

## Screenshot Checklist

| # | Screenshot | Filename |
|---|---|---|
| 1 | Synapse Studio — workspace home with Data hub open | Step_01_Synapse_Studio_Home.png |
| 2 | Serverless SQL script — preview of cleaned Parquet data (Query 1 results) | Step_02_Serverless_Preview_Results.png |
| 3 | Average score by performance band — query results (Query 2) | Step_03_Avg_Score_By_Band.png |
| 4 | Pass / fail counts — query results (Query 3) | Step_04_Pass_Fail_Counts.png |
| 5 | Dedicated SQL Pool — same aggregation on the loaded table (Query 4) | Step_05_Dedicated_Pool_Results.png |
| 6 | Second source — passenger CSV preview via OPENROWSET (Query 5) | Step_06_Passenger_CSV_Preview.png |
| 7 | Power BI Desktop — Get Data, Azure Synapse Analytics SQL connector | Step_07_PowerBI_Get_Data_Synapse.png |
| 8 | Power BI connection dialog — server name and DirectQuery selected | Step_08_PowerBI_DirectQuery_Selected.png |
| 9 | Power BI report — performance band distribution visual | Step_09_PowerBI_Band_Distribution.png |
| 10 | Power BI report — average score visual and pass-rate KPI card | Step_10_PowerBI_Score_KPI.png |
| 11 | Power BI report — filter changed, visual updated live (DirectQuery) | Step_11_PowerBI_Live_Filter_Update.png |
| 12 | Synapse Studio — dedicated SQL pool paused after the lab | Step_12_Dedicated_Pool_Paused.png |

Note: screenshots are not in this folder yet — add them under `screenshots/` using the filenames above. Do not include a screenshot that shows a password, key, or other credential.

## Result

The serverless SQL queries ran against the Experiment 6 cleaned Parquet data in ADLS Gen2 and returned the average score by performance band and the pass/fail counts; the dedicated pool variant returned the same aggregation from the loaded `student_performance` table; and the Experiment 3 passenger CSV was queried as a second source through the same serverless endpoint. Power BI Desktop connected to Synapse with DirectQuery and rendered the performance band distribution, average score, and pass-rate KPI visuals, with each filter interaction re-querying Synapse live. The dedicated SQL pool was paused after the lab. Record the observed value here for the band averages, the pass/fail counts, and the pass rate shown in the report.

## Key Learning

This experiment demonstrates live analytics on Azure: Synapse serverless SQL queries lake data in place without a loading step, the dedicated pool serves the same data from loaded tables for heavier repeated queries, and Power BI DirectQuery turns either endpoint into visuals that stay current because every interaction re-queries the source — with scheduled refresh only relevant to Import mode, and the dedicated pool paused afterwards to keep the lab inside the free tier.
