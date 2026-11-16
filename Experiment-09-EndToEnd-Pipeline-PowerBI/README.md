# Experiment 9: Evaluate a full data pipeline from raw data ingestion to visualization in Power BI

**Course:** Cloud Analytics (25MCAR0141)
**Course Outcome:** CO3
**Target document:** CA_Exp09_Pipeline_Evaluation.pdf (also in this folder)

## Aim

To evaluate a complete end-to-end data pipeline — from raw data ingestion in Azure Blob Storage, through orchestration in Azure Data Factory and transformation in Azure Databricks, to visualization in Power BI — by running the pipeline built in Experiment 6, verifying the data at every stage, and recording the observed results against defined evaluation criteria.

## Objectives

- Trigger the Experiment 6 pipeline (`PL_ADF_Databricks`) and observe the full run from end to end.
- Verify each pipeline stage: Blob Storage source, ADF Copy Data activity, ADLS Gen2 `rawdata`, Databricks TransformData notebook, and ADLS Gen2 `output` Parquet.
- Compare row counts across stages (source CSV vs `rawdata` vs cleaned Parquet) to check completeness.
- Spot-check data quality in the curated output: null handling, duplicate removal, and `performance_band` / `result` correctness.
- Connect Power BI to the curated output and build visuals from it.
- Confirm the Power BI visuals match the Parquet aggregates.
- Record every observed value in `evaluation/evaluation_checklist.md` and judge each criterion Pass or Fail.

## Architecture

```text
Azure Blob Storage (student_performance.csv)
        |  Copy Data activity (CopyRawDataToADLS)
        v
ADLS Gen2 (calablake141 / rawdata)
        |  Databricks Notebook activity, on Copy success
        v
Azure Databricks (calab-databricks-141)
        |  TransformData notebook: clean + feature engineering
        v
ADLS Gen2 (calablake141 / output)
        |  output/student_performance_cleaned (Parquet)
        v
Power BI
        |  Connect to curated output, build visuals
        v
Dashboard: performance bands, results, score distribution
```

Nothing new is built in this experiment — the pipeline already exists from Experiment 6 (ADF `calab-adf-141`, Databricks `calab-databricks-141`, ADLS Gen2 `calablake141`, resource group `25MCAR0141`, centralindia). The work here is to run it, watch each hop, and prove — with the numbers from the actual run — that the data arrives in Power BI complete, clean, and correct.

## Architecture & Component Roles

| Component | Resource Name | Role / Description |
|---|---|---|
| Resource Group | 25MCAR0141 | Logical container for all Azure experiment resources |
| Blob Storage | calablake141 (source container) | Raw ingestion point holding `student_performance.csv` |
| Data Factory | calab-adf-141 | Orchestrator executing the ELT pipeline |
| Pipeline | PL_ADF_Databricks | Copy Data → Databricks Notebook, success-dependency chained |
| Storage Account | calablake141 | ADLS Gen2 hosting rawdata (input) and output (transformed) containers |
| Databricks Workspace | calab-databricks-141 | Spark platform executing the TransformData notebook |
| Linked Service | LS_Databricks | ADF ↔ Databricks connection (MSI auth, job cluster) |
| Power BI | Power BI Desktop / Service | Visualization layer over the curated Parquet output |

## Services Used

- Azure Data Factory
- Azure Databricks (PySpark)
- Azure Blob Storage
- Azure Data Lake Storage Gen2
- Power BI Desktop (or Power BI Service)
- Azure Portal / ADF Studio
- Azure Cost Management (for recording the run's cost)

## Procedure

### Step 1 — Confirm the Experiment 6 pipeline is in place

Open ADF Studio (`calab-adf-141`) and confirm pipeline `PL_ADF_Databricks` exists with its two activities: `CopyRawDataToADLS` (Copy Data) and `RunTransformDataNotebook` (Databricks Notebook), chained by a success dependency. Confirm the source file `student_performance.csv` is present in Blob Storage.

### Step 2 — Note the source row count

Open the source CSV and record its row count (excluding the header) in `evaluation/evaluation_checklist.md`. This is the baseline every later count is compared against.

### Step 3 — Trigger the pipeline

In ADF Studio, select `PL_ADF_Databricks` → Add Trigger → Trigger Now. Note the trigger time — the run's start time is the beginning of the end-to-end latency measurement.

### Step 4 — Monitor the run in ADF

Monitor → Pipeline Runs → follow the run. Record the status and duration of each activity (`CopyRawDataToADLS`, then `RunTransformDataNotebook`) and the total pipeline run duration in the checklist.

### Step 5 — Verify the rawdata stage

In Storage Explorer (or the portal), open `calablake141/rawdata` and confirm the copied CSV is present. Record the row count of the copied file and compare it with the source count from Step 2.

### Step 6 — Verify the Databricks transform

Open the Databricks workspace (`calab-databricks-141`) and check the TransformData notebook run output: rows read, rows after cleaning, and confirmation that the score features were added. Note anything the notebook reports (for example, if no score column was found, the data is written without score features).

### Step 7 — Verify the curated output

Open `calablake141/output/student_performance_cleaned` and confirm the Parquet files are present. Read the Parquet output (from the notebook or a quick query) and record the final row count. Compare it with the source and rawdata counts and account for any difference (duplicates dropped, for example).

### Step 8 — Spot-check data quality

On a small sample of rows from the cleaned output, check: no nulls remain unhandled, no duplicate rows survive, and `performance_band` and `result` are correct for the row's scores (Excellent >= 85, Good >= 70, Average >= 50, otherwise Needs Improvement; Pass when average >= 40, otherwise Fail). Record the sample size and what was found in the checklist.

### Step 9 — Connect Power BI to the curated output

In Power BI Desktop, connect to the curated Parquet output in `calablake141/output/student_performance_cleaned` (Get Data → Parquet, or via the ADLS Gen2 connector). Sign in with the usual organizational account — do not paste any storage key or connection string into the report or this folder. Load the data and confirm the row count Power BI reports matches the Parquet row count from Step 7.

### Step 10 — Build the visuals

Build at least: a bar chart of students per `performance_band`, a chart of Pass vs Fail (`result`), and a score distribution visual (for example, average score by band or a histogram of `average_score`). Add a card showing the total student count.

### Step 11 — Verify the visuals against the source aggregates

Compare the totals Power BI shows (total students, count per band, Pass/Fail split) with the aggregates computed from the Parquet output in Step 7. Record whether they match in the checklist.

### Step 12 — Record freshness and cost

Record the time from pipeline trigger (Step 3) to the finished Power BI visual — that is the ingestion-to-visualization freshness for this run. In Azure Cost Management, record the cost of the resources used by this run (note the scope and period checked; do not estimate figures).

### Step 13 — Judge each criterion and finish the checklist

For every criterion in `evaluation/evaluation_checklist.md`, fill in the observed value from this run and mark Pass or Fail. Any Fail gets a short note on what was observed and what would need fixing.

## Evaluation Criteria

The full fill-in checklist is in [`evaluation/evaluation_checklist.md`](evaluation/evaluation_checklist.md). Summary of what is evaluated:

| Criterion | What is checked |
|---|---|
| End-to-end latency | Total pipeline run duration, from trigger to both activities Succeeded |
| Completeness | Row counts at each hop: source CSV vs `rawdata` vs cleaned Parquet |
| Data accuracy / quality | Null handling, duplicate removal, `performance_band` / `result` correctness on spot-checked rows |
| Freshness | Time from ingestion (pipeline trigger) to the finished Power BI visual |
| Reliability | Both activities Succeeded; success dependency means a failed copy never triggers a transform on stale or missing input |
| Cost | Cost of the run's resources, recorded from Cost Management |
| Visualization correctness | Power BI totals match the Parquet aggregates |

No observed values are written anywhere in this folder in advance — every number comes from the actual run and is recorded in the checklist at evaluation time.

## Screenshot Checklist

| # | Screenshot | Filename |
|---|---|---|
| 1 | ADF Studio — pipeline PL_ADF_Databricks canvas (Copy → Notebook chain) | Step_01_Pipeline_Canvas.png |
| 2 | Trigger Now — pipeline triggered | Step_02_Pipeline_Triggered.png |
| 3 | Monitor — pipeline run succeeded (both activities green) | Step_03_Pipeline_Run_Succeeded.png |
| 4 | Copy Data activity run details (rows read/written, duration) | Step_04_Copy_Activity_Run_Details.png |
| 5 | Databricks Notebook activity run details (with output) | Step_05_Notebook_Activity_Output.png |
| 6 | ADLS Gen2 — rawdata container with copied CSV | Step_06_ADLS_Rawdata_Container.png |
| 7 | ADLS Gen2 — output/student_performance_cleaned Parquet files | Step_07_ADLS_Output_Parquet.png |
| 8 | Databricks notebook — TransformData output (cleaned rows, score features) | Step_08_Databricks_TransformData_Output.png |
| 9 | Power BI — data loaded, row count matching the Parquet output | Step_09_PowerBI_Data_Loaded.png |
| 10 | Power BI — dashboard visuals (performance bands, Pass/Fail, score distribution) | Step_10_PowerBI_Dashboard.png |
| 11 | Cost Management — cost of the run's resources | Step_11_Cost_Management.png |

Note: screenshots are not in this folder yet — add them under `screenshots/` using the filenames above. Do not include a screenshot that shows a token, key, connection string, or other credential.

## Result

A successful evaluation demonstrates the full pipeline working end to end: the Experiment 6 pipeline runs to completion with both activities succeeding, the data is verified at every stage from Blob Storage source through ADLS Gen2 raw and curated layers, the cleaned Parquet output is confirmed complete and correct against the source, and Power BI visuals built on that output reproduce the same aggregates. The completed checklist in `evaluation/evaluation_checklist.md` is the evidence — it records the observed latency, counts, quality checks, freshness, reliability, cost, and visualization verification for the run.

## Key Learning

This experiment shows that building a pipeline is only half the work — evaluating it is the other half. A pipeline earns trust stage by stage: counts compared at every hop, quality spot-checked on real rows, the success dependency proving a failed copy can never trigger a transform on bad input, and the final visuals checked back against the curated data they claim to show. Power BI is only as truthful as the pipeline behind it, and the evaluation checklist is what makes that claim checkable.
