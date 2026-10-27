# Experiment 6: End-to-End Data Pipeline Orchestration using Azure Data Factory and Azure Databricks

**Course:** Cloud Analytics (25MCAR0141)
**Course Outcome:** CO3
**Target document:** CA_Exp06_ADF_Databricks.pdf (also in this folder)

## Aim

To integrate Azure Data Factory with Azure Databricks for end-to-end data pipeline orchestration, where ADF triggers a Databricks notebook to preprocess and transform data ingested from Azure Data Lake Storage Gen2.

## Objectives

- Create ADF Linked Services for Blob Storage, ADLS Gen2, and Azure Databricks.
- Build an ADF pipeline with Copy Data activity followed by Databricks Notebook activity.
- Configure success-dependency chaining between pipeline activities.
- Implement PySpark data cleaning and feature engineering in a Databricks notebook.
- Validate the transformed Parquet output in ADLS Gen2.
- Monitor pipeline runs and activity status in ADF Studio.

## Architecture

```text
Azure Blob Storage (student_performance.csv)
        |  Copy Data activity
        v
ADLS Gen2 (calablake141 / rawdata)
        |  Databricks Notebook activity (on Copy success)
        v
Azure Databricks (calab-databricks-141)
        |  TransformData notebook: clean + feature engineering
        v
ADLS Gen2 (calablake141 / output)
        |
        v
output/student_performance_cleaned (Parquet)
```

ADF (`calab-adf-141`) is the orchestrator: it does not transform the data itself — it copies it, then triggers the notebook, and only runs the notebook if the copy succeeded.

## Architecture & Component Roles

| Component | Resource Name | Role / Description |
|---|---|---|
| Resource Group | 25MCAR0141 | Logical container for all Azure experiment resources |
| Data Factory | calab-adf-141 | Cloud data orchestration engine executing the ELT pipeline |
| Storage Account | calablake141 | ADLS Gen2 hosting rawdata (input) and output (transformed) containers |
| Databricks Workspace | calab-databricks-141 | Apache Spark platform executing the TransformData notebook |
| Linked Service | LS_Databricks | ADF ↔ Databricks connection (MSI auth, job cluster) |
| Pipeline | PL_ADF_Databricks | Orchestrates Copy Data → Databricks Notebook activities |

## Services Used

- Azure Data Factory
- Azure Databricks (PySpark)
- Azure Blob Storage
- Azure Data Lake Storage Gen2
- Azure Portal / ADF Studio

## Procedure

### Step 1 — Open ADF Studio

Azure Portal → `calab-adf-141` → Launch Studio.

### Step 2 — Create Linked Service — Blob Storage

Manage → Linked Services → + New → Azure Blob Storage → name `LS_BlobSource` → select `calablake141`.

### Step 3 — Create Linked Service — ADLS Gen2

\+ New → Azure Data Lake Storage Gen2 → name `LS_ADLS_Sink` → select `calablake141`.

### Step 4 — Create Linked Service — Databricks

\+ New → Azure Databricks → name `LS_Databricks` → workspace URL: `adb-7405609713574305.5.azuredatabricks.net` → New job cluster → Runtime 14.3, Standard_DS3_v2, 1 worker. Authentication: MSI (see `linkedService/LS_Databricks.json` — replace its `<workspace resource ID for calab-databricks-141>` placeholder with the workspace resource ID from the portal; no token or key is stored in this repo).

### Step 5 — Create Source Dataset

Author → Datasets → + New → DelimitedText → name `DS_BlobSource_CSV` → linked service `LS_BlobSource` → file `student_performance.csv` (see `dataset/DS_BlobSource_CSV.json` — replace its `<source-container>` placeholder with the actual Blob container).

### Step 6 — Create Sink Dataset

\+ New → DelimitedText → name `DS_ADLS_Sink_CSV` → linked service `LS_ADLS_Sink` → container `rawdata` (see `dataset/DS_ADLS_Sink_CSV.json`).

### Step 7 — Upload TransformData Notebook

In Databricks Studio, import `TransformData.py` (in this folder) as a notebook.

### Step 8 — Create Pipeline

Author → Pipelines → + New → name `PL_ADF_Databricks` (see `pipeline/PL_ADF_Databricks.json`).

### Step 9 — Add Copy Data Activity

Drag Copy Data → Source: `DS_BlobSource_CSV` → Sink: `DS_ADLS_Sink_CSV`.

### Step 10 — Add Databricks Notebook Activity

Drag Databricks Notebook → connect after Copy Data (success dependency) → select `LS_Databricks` → browse notebook `/Users/.../TransformData` (replace `/Users/<username>/TransformData` in the pipeline JSON with the actual notebook path in the workspace).

### Step 11 — Validate & Publish

Click Validate → Publish All.

### Step 12 — Trigger Pipeline

Add Trigger → Trigger Now → run the pipeline.

### Step 13 — Monitor & Verify

Monitor → Pipeline Runs → verify both activities show Succeeded. Check `calablake141/output/student_performance_cleaned` for Parquet files.

## Pipeline Activity Chain

```text
CopyRawDataToADLS (Copy Data)
    │
    ├── Source: DS_BlobSource_CSV (Blob Storage)
    ├── Sink:   DS_ADLS_Sink_CSV (ADLS Gen2 rawdata)
    │
    └── On Success ──→ RunTransformDataNotebook (Databricks Notebook)
                            │
                            ├── Linked Service: LS_Databricks
                            ├── Notebook: /Users/.../TransformData
                            └── Output: ADLS Gen2 output/ (Parquet + CSV)
```

The success dependency is the key orchestration point: in `pipeline/PL_ADF_Databricks.json`, `RunTransformDataNotebook` has `"dependsOn": [{"activity": "CopyRawDataToADLS", "dependencyConditions": ["Succeeded"]}]`, so a failed copy never triggers a transform on stale or missing input.

## ADF Pipeline Definition

The pipeline JSON definitions are available in:

- Pipeline: [`pipeline/PL_ADF_Databricks.json`](pipeline/PL_ADF_Databricks.json)
- Linked Service: [`linkedService/LS_Databricks.json`](linkedService/LS_Databricks.json)

Dataset definitions referenced by the pipeline are also included:

- [`dataset/DS_BlobSource_CSV.json`](dataset/DS_BlobSource_CSV.json)
- [`dataset/DS_ADLS_Sink_CSV.json`](dataset/DS_ADLS_Sink_CSV.json)

## TransformData Notebook — Code Highlights

Full notebook: [`TransformData.py`](TransformData.py)

**Read (from ADLS Gen2, after the Copy activity):**

```python
df = spark.read.option("header", True).option("inferSchema", True).csv(INPUT_PATH)
# INPUT_PATH = abfss://rawdata@calablake141.dfs.core.windows.net/student_performance.csv
```

**Data cleaning:**

- Strip whitespace from column names and string values.
- Drop exact duplicate rows.
- Fill nulls: numeric columns with the column mean, string columns with `"Unknown"`.

**Feature engineering:**

Score-like columns are detected by name (`score` / `marks` / `grade`), so the step adapts to the actual `student_performance.csv` layout. When such columns exist, the notebook adds:

- `total_score` and `average_score`
- `performance_band`: Excellent (≥ 85), Good (≥ 70), Average (≥ 50), otherwise Needs Improvement
- `result`: Pass (average ≥ 40), otherwise Fail

If no score column is present, the cleaned data is written without score features and the notebook reports that.

**Write (transformed output to ADLS Gen2):**

```python
df.write.mode("overwrite").parquet(PARQUET_OUTPUT_PATH)
# abfss://output@calablake141.dfs.core.windows.net/student_performance_cleaned
df.coalesce(1).write.mode("overwrite").option("header", True).csv(CSV_OUTPUT_PATH)
```

## Screenshot Checklist

| # | Screenshot | Filename |
|---|---|---|
| 1 | ADF Studio — Linked Services list (LS_BlobSource, LS_ADLS_Sink, LS_Databricks) | Step_01_ADF_Linked_Services.png |
| 2 | LS_Databricks configuration (workspace URL, cluster config) | Step_02_LS_Databricks_Config.png |
| 3 | Dataset DS_BlobSource_CSV configuration | Step_03_Dataset_Source_Config.png |
| 4 | Pipeline canvas — Copy Data → Databricks Notebook chain | Step_04_Pipeline_Canvas.png |
| 5 | Copy Data activity settings (source & sink) | Step_05_Copy_Activity_Settings.png |
| 6 | Databricks Notebook activity settings (notebook path) | Step_06_Notebook_Activity_Settings.png |
| 7 | Pipeline validation — no errors | Step_07_Pipeline_Validation.png |
| 8 | Trigger Now — pipeline triggered | Step_08_Pipeline_Triggered.png |
| 9 | Monitor — Pipeline run succeeded (both activities green) | Step_09_Pipeline_Run_Succeeded.png |
| 10 | Copy Data activity run details | Step_10_Copy_Activity_Run_Details.png |
| 11 | Databricks Notebook activity run details (with output) | Step_11_Notebook_Activity_Output.png |
| 12 | ADLS Gen2 — rawdata container with uploaded CSV | Step_12_ADLS_Rawdata_Container.png |
| 13 | ADLS Gen2 — output/student_performance_cleaned Parquet files | Step_13_ADLS_Output_Parquet.png |
| 14 | Databricks notebook — TransformData output display | Step_14_Databricks_TransformData_Output.png |

Note: screenshots are not in this folder yet — add them under `screenshots/` using the filenames above. Do not include a screenshot that shows a token, key, or other credential.

## Result

The ADF pipeline ran end to end: Copy Data moved `student_performance.csv` from Blob Storage into ADLS Gen2 `rawdata`, and on its success the Databricks Notebook activity ran `TransformData`, cleaning the data and adding score features, with the transformed output validated as Parquet files in `calablake141/output/student_performance_cleaned`. Both activities showed Succeeded in ADF Monitor.

## Key Learning

This experiment demonstrates ELT orchestration on Azure: ADF as the control plane (linked services, datasets, success-dependency chaining, monitoring) and Databricks as the compute plane (PySpark cleaning and feature engineering), with ADLS Gen2 as the shared raw and transformed storage layer between them.
