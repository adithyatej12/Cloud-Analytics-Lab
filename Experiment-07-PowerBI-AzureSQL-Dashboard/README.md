# Experiment 7: Connect Power BI to Azure SQL and create a dashboard with real-time insights

**Course:** Cloud Analytics (25MCAR0141)
**Course Outcome:** CO3
**Target document:** CA_Exp07_PowerBI_AzureSQL.pdf (also in this folder)

## Aim

To connect Power BI Desktop to an Azure SQL Database, build DAX measures and a dashboard over student performance data, and compare Import mode with scheduled refresh against DirectQuery for near-real-time insights.

## Objectives

- Create an Azure SQL Database in the lab resource group and configure a firewall rule.
- Create and load a `student_performance` table using T-SQL.
- Connect Power BI Desktop to Azure SQL Database (Get Data -> Azure SQL Database).
- Build DAX measures for Average Score and Pass Rate %.
- Build a dashboard with a bar chart of average score by subject, KPI cards, and a slicer by student.
- Compare Import mode with scheduled refresh against DirectQuery for near-real-time data.
- State honestly what DirectQuery can and cannot do for real-time reporting.

## Architecture

```text
Azure SQL Database (calab-sqldb-141)
        |  Table: student_performance
        |  Server: <server-name> (placeholder - see Procedure)
        v
Power BI Desktop - Get Data -> Azure SQL Database
        |
        +-- Import mode: data copied into the .pbix, refreshed on schedule
        |
        +-- DirectQuery mode: every interaction queries the live database
        |
        v
Power BI Dashboard
        |  Bar chart: average score by subject
        |  KPI cards: average score, pass rate %
        |  Slicer: by student
        v
Published to Power BI service (optional) - scheduled refresh / live DirectQuery
```

The database is the single source of truth. Power BI never owns the data — in Import mode it holds a snapshot that goes stale until the next refresh, and in DirectQuery mode it holds no data at all and asks the database again on every click.

## Architecture & Component Roles

| Component | Resource Name | Role / Description |
|---|---|---|
| Resource Group | 25MCAR0141 | Logical container for all Azure experiment resources |
| SQL Server (logical) | `<server-name>` | Logical server hosting the database (replace the placeholder with the server name created in the portal) |
| SQL Database | calab-sqldb-141 | Azure SQL Database holding the `student_performance` table |
| Firewall Rule | `<firewall-rule-name>` | Allows the lab machine's public IP to reach the SQL server |
| Storage Account | calablake141 | ADLS Gen2 from Experiments 5-6 (rawdata / output) - the source the SQL table mirrors |
| Databricks Workspace | calab-databricks-141 | Spark platform from Experiments 5-6 (upstream transforms) |
| Data Factory | calab-adf-141 | Orchestration engine from Experiment 6 (upstream pipeline) |
| Power BI Desktop | (local) | Report authoring tool - connects to Azure SQL, defines DAX measures and visuals |
| Power BI Service | (optional) | Publishing target for scheduled refresh and sharing |

## Services Used

- Azure SQL Database
- Power BI Desktop (and optionally the Power BI service)
- Azure Portal
- Azure Data Lake Storage Gen2 (upstream, from Experiments 5-6)
- Azure Databricks / Azure Data Factory (upstream, from Experiments 5-6)

## Procedure

### Step 1 — Create the SQL Database

Azure Portal -> SQL databases -> Create -> Resource group `25MCAR0141`, Region `centralindia` -> Database name `calab-sqldb-141` -> Server: Create new, name `<server-name>` (replace with the server name you create; server names must be globally unique) -> Authentication: SQL authentication with admin login `<username>` and password `<password>` (choose them in the portal; do not write real credentials anywhere in this repo).

### Step 2 — Configure the Firewall Rule

SQL server -> Networking -> add a firewall rule named `<firewall-rule-name>` allowing the lab machine's public IP address. (The portal offers an "Add your client IPv4 address" button — use that rather than opening a wide range.)

### Step 3 — Open the Query Editor

SQL database `calab-sqldb-141` -> Query editor -> sign in with `<username>` / `<password>`.

### Step 4 — Create and Load the Table

Run `sql/create_student_performance.sql` (in this folder) in the query editor. It creates the `student_performance` table and inserts 12 sample rows.

### Step 5 — Verify the Data

Run the queries in `sql/sample_queries.sql` — average score by subject, pass rate (average >= 40), and top students. Confirm 12 rows are present before moving to Power BI.

### Step 6 — Connect Power BI Desktop to Azure SQL

Power BI Desktop -> Get Data -> Azure SQL Database -> Server: `<server-name>.database.windows.net` -> Database: `calab-sqldb-141` -> sign in with `<username>` / `<password>`. (Use the placeholders here; never paste a real connection string or password into a file or screenshot.)

### Step 7 — Choose Import Mode First

Select Import, then select the `student_performance` table and Load. The data is copied into the `.pbix` file — it is a snapshot, and it only changes when the dataset is refreshed.

### Step 8 — Create DAX Measures

In the Data view, create the measures from the DAX highlights below: `Average Score` and `Pass Rate %`.

### Step 9 — Build the Dashboard Visuals

- Clustered bar chart: average score by subject (Math, English, Science).
- KPI cards: Average Score and Pass Rate %.
- Slicer: by student (`student_name`), so selecting a student filters the whole page.

### Step 10 — Publish and Schedule Refresh (Import Mode)

Publish the report to the Power BI service, then set a scheduled refresh on the dataset (for example daily). Until a refresh runs, the published dashboard shows the snapshot from publish time — record the observed refresh time here.

### Step 11 — Repeat the Connection in DirectQuery Mode

Back in Power BI Desktop, connect again to the same database, this time choosing DirectQuery. Rebuild the same visuals (or copy the report pages). No data is imported — every slicer click and filter sends a live query to `calab-sqldb-141`.

### Step 12 — Test Near-Real-Time Behaviour

With the DirectQuery report open, update one score in the SQL database (for example, change one student's math score in the query editor), then interact with the report — change the slicer or refresh the visual. The visual updates from the live query. Record the observed behaviour here: note what changed and roughly how long the visual took to refresh (record the observed value here).

### Step 13 — Compare Import vs DirectQuery

Note the trade-off in your own words: Import is fast and supports the full DAX feature set but shows data only as fresh as the last refresh; DirectQuery is always current but every interaction hits the database, so it is slower and some DAX functions are unavailable. Record the observed refresh behaviour for each mode here.

## SQL Highlights

### Create and Load the Table

Full script: [`sql/create_student_performance.sql`](sql/create_student_performance.sql)

```sql
CREATE TABLE student_performance (
    student_id INT PRIMARY KEY,
    student_name NVARCHAR(100) NOT NULL,
    math_score INT NOT NULL,
    english_score INT NOT NULL,
    science_score INT NOT NULL
);
```

The script then inserts 12 sample rows (scores out of 100, a realistic spread including students below the pass mark). The table mirrors the `student_performance` data used in Experiments 5 and 6, so the dashboard reports on the same dataset the earlier pipelines processed.

### Sample Queries

Full script: [`sql/sample_queries.sql`](sql/sample_queries.sql)

**Average score by subject:**

```sql
SELECT
    AVG(CAST(math_score AS FLOAT)) AS avg_math,
    AVG(CAST(english_score AS FLOAT)) AS avg_english,
    AVG(CAST(science_score AS FLOAT)) AS avg_science
FROM student_performance;
```

**Pass rate (average >= 40):**

```sql
SELECT
    COUNT(*) AS total_students,
    SUM(CASE WHEN (math_score + english_score + science_score) / 3.0 >= 40 THEN 1 ELSE 0 END) AS passed,
    100.0 * SUM(CASE WHEN (math_score + english_score + science_score) / 3.0 >= 40 THEN 1 ELSE 0 END) / COUNT(*) AS pass_rate_pct
FROM student_performance;
```

**Top students by average score:**

```sql
SELECT TOP 5
    student_name,
    (math_score + english_score + science_score) / 3.0 AS average_score
FROM student_performance
ORDER BY average_score DESC;
```

Run these in the query editor and record the observed values here — do not copy numbers from anywhere else; the values depend on the data actually loaded.

## DAX Highlights

Create these measures in Power BI Desktop (Data view -> New measure). They are written against the imported `student_performance` table.

**Average Score:**

```dax
Average Score = AVERAGEX(
    student_performance,
    ( student_performance[math_score]
      + student_performance[english_score]
      + student_performance[science_score] ) / 3
)
```

**Pass Rate %:**

```dax
Pass Rate % =
VAR PassedStudents = COUNTROWS(
    FILTER(
        student_performance,
        ( student_performance[math_score]
          + student_performance[english_score]
          + student_performance[science_score] ) / 3 >= 40
    )
)
RETURN DIVIDE( PassedStudents, COUNTROWS( student_performance ) ) * 100
```

`AVERAGEX` is used instead of `AVERAGE` because the average must be computed per student first (across that student's three subjects) and then averaged — averaging the three subject columns directly would give a different number. `DIVIDE` is used instead of `/` so the measure returns blank rather than an error if the table is ever empty.

## A Note on "Real-Time"

DirectQuery queries the live database on each interaction, so a dashboard visual updates when the underlying data changes and the user interacts with the report — that is near-real-time, not streaming. True streaming (a visual that updates by itself, seconds after data arrives, with no user interaction) would need a streaming dataset — for example Power BI streaming datasets fed by Azure Stream Analytics or an Event Hub pipeline like the one in Experiment 5 — and that is not what this experiment builds. Do not describe the DirectQuery dashboard as streaming; describe it as live-querying the database on each interaction.

## Screenshot Checklist

| # | Screenshot | Filename |
|---|---|---|
| 1 | Azure Portal — SQL database calab-sqldb-141 overview | Step_01_SQL_Database_Overview.png |
| 2 | SQL server firewall rule configuration | Step_02_Firewall_Rule_Config.png |
| 3 | Query editor — create_student_performance.sql executed (12 rows inserted) | Step_03_Table_Created_Rows_Inserted.png |
| 4 | Query editor — sample queries output (average by subject, pass rate, top students) | Step_04_Sample_Queries_Output.png |
| 5 | Power BI Desktop — Get Data, Azure SQL Database connection dialog | Step_05_PowerBI_Get_Data_Connection.png |
| 6 | Power BI Desktop — Navigator showing student_performance table, Import mode selected | Step_06_PowerBI_Navigator_Import.png |
| 7 | Power BI Desktop — DAX measures (Average Score, Pass Rate %) in the Data view | Step_07_PowerBI_DAX_Measures.png |
| 8 | Power BI Desktop — dashboard page (bar chart, KPI cards, student slicer) | Step_08_PowerBI_Dashboard.png |
| 9 | Power BI service — published report with scheduled refresh configured | Step_09_PowerBI_Scheduled_Refresh.png |
| 10 | Power BI Desktop — DirectQuery connection to the same database | Step_10_PowerBI_DirectQuery_Connection.png |
| 11 | DirectQuery test — score updated in SQL, visual updated after interacting with the report | Step_11_DirectQuery_Live_Update.png |
| 12 | Side-by-side note or view comparing Import vs DirectQuery behaviour | Step_12_Import_vs_DirectQuery.png |

Note: screenshots are not in this folder yet — add them under `screenshots/` using the filenames above. Do not include a screenshot that shows a password, connection string, or other credential — mask the sign-in fields before capturing Steps 5 and 10.

## Result

A successful run demonstrates: an Azure SQL Database (`calab-sqldb-141`) holding a 12-row `student_performance` table; Power BI Desktop connected to it in both Import and DirectQuery modes; DAX measures for Average Score and Pass Rate %; and a dashboard with a bar chart of average score by subject, KPI cards, and a student slicer. In Import mode the dashboard shows the snapshot from the last refresh; in DirectQuery mode the visuals query the live database on each interaction, so an updated score appears after interacting with the report. Record the observed values here: the average score by subject, the pass rate, and the refresh behaviour observed in each mode.

## Key Learning

This experiment demonstrates BI reporting on Azure: Azure SQL Database as the single source of truth, Power BI as the presentation layer, DAX as the calculation layer, and the Import-vs-DirectQuery trade-off at the centre — Import is fast but only as fresh as its last refresh, DirectQuery is always current but queries the database on every interaction. It also draws the honest line between near-real-time (live queries on interaction) and true streaming (automatic push updates, which would need a streaming dataset).
