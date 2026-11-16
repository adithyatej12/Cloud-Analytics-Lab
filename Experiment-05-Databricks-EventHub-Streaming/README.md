# Experiment 5: Real-Time Streaming Data Processing using Databricks & Azure Event Hub

**Course:** Cloud Analytics (25MCAR0141)
**Course Outcome:** CO3
**Target document:** CA_Exp05_Streaming.pdf (also in this folder)

## Aim

To process real-time streaming data using Azure Databricks and Azure Event Hub by ingesting a live data stream, processing it using Structured Streaming in PySpark, and displaying the output in a Databricks notebook.

## Objectives

- Create and configure an Azure Event Hub namespace and entity with SAS policies.
- Implement a Python producer script that simulates real-time student activity events.
- Read the stream in Azure Databricks using the Event Hub Spark connector.
- Parse JSON event payloads and apply schema enforcement.
- Perform tumbling window aggregations (event counts, average scores per student).
- Write streaming output to ADLS Gen2 in Parquet format with checkpointing.

## Architecture

```text
Local Python producer (producer.py)
        |  50 student activity events (JSON)
        v
Azure Event Hub Namespace (calab-eventhub-ns-141)
        |  Event Hub entity, 2 partitions
        v
Azure Databricks (calab-databricks-141)
        |  Structured Streaming + Event Hub Spark connector
        |  Parse JSON -> schema enforcement
        |  Tumbling window (5 min) + watermark (2 min)
        v
ADLS Gen2 (calablake141)
        |  Parquet output + checkpoint
        v
output/streaming_events
```

## Architecture & Component Roles

| Component | Resource Name | Role / Description |
|---|---|---|
| Resource Group | 25MCAR0141 | Logical container for all Azure experiment resources |
| Event Hub Namespace | calab-eventhub-ns-141 | Managed event ingestion service (Basic SKU, centralindia) |
| Event Hub | calab-eventhub-141 | Event stream entity (2 partitions, 1-hour retention) |
| SAS Policy | DatabricksPolicy | Shared Access Policy with Send + Listen permissions |
| Databricks Workspace | calab-databricks-141 | Spark analytics platform running Structured Streaming notebooks |
| Storage Account | calablake141 | ADLS Gen2 — output sink for streaming Parquet files |

## Services Used

- Azure Event Hubs
- Azure Databricks (Spark Structured Streaming, PySpark)
- Azure Data Lake Storage Gen2
- Azure Portal

## Procedure

### Step 1 — Create Event Hub Namespace

Azure Portal → Event Hubs → Create Namespace `calab-eventhub-ns-141` in resource group `25MCAR0141` (Basic SKU, centralindia).

### Step 2 — Create Event Hub Entity

Inside the namespace → + Event Hub → Name: `calab-eventhub-141`, Partitions: 2 (retention: 1 hour).

### Step 3 — Create SAS Policy

Event Hub → Shared Access Policies → Add `DatabricksPolicy` with Send + Listen permissions.

### Step 4 — Copy Connection String

Copy the Primary Connection String from `DatabricksPolicy`. Paste it into the notebook placeholder only — do not commit a real connection string to GitHub (see the placeholder in `Exp05_Databricks_Streaming.py` and `producer.py`).

### Step 5 — Open Databricks Studio

Navigate to `calab-databricks-141` → Launch Workspace.

### Step 6 — Create Cluster

Compute → Create Cluster → Single Node, Runtime 14.3 LTS, Standard_DS3_v2.

### Step 7 — Install Maven Library

Cluster → Libraries → Install New → Maven → `com.microsoft.azure:azure-eventhubs-spark_2.12:2.3.22`.

### Step 8 — Import Streaming Notebook

Upload `Exp05_Databricks_Streaming.py` (in this folder) and paste the connection string into its placeholder.

### Step 9 — Run Producer Script

Locally run `python producer.py` to send 50 student activity events (see `producer.py` — install with `pip install azure-eventhub` first).

### Step 10 — Start Streaming Notebook

Run all cells — observe real-time events, parsed JSON, and windowed aggregations.

### Step 11 — Verify Output

Check `calablake141/output/streaming_events` for Parquet files (and the checkpoint location alongside it).

### Step 12 — Stop Stream & Terminate Cluster

Stop the streaming query (`streaming_query.stop()`), then terminate the cluster to save cost.

## Code Highlights

### Producer — Send Events to Event Hub

Full script: [`producer.py`](producer.py)

```python
from azure.eventhub import EventHubProducerClient, EventData

event = {"student_name": "Abhi", "event_type": "quiz_submit", "score": 85, ...}
producer.send_batch(event_data_batch)
```

The full script generates 50 events across several students and event types (`login`, `video_view`, `quiz_submit`, `assignment_submit`, `discussion_post`). A `score` is sent only for `quiz_submit` events; other events carry a null score, which `avg()` ignores in the aggregation.

### Consumer — Structured Streaming from Event Hub

Full notebook: [`Exp05_Databricks_Streaming.py`](Exp05_Databricks_Streaming.py)

```python
raw_stream = spark.readStream.format("eventhubs").options(**ehConf).load()
parsed = raw_stream.select(from_json(col("body").cast("string"), schema).alias("event"))
```

The notebook aliases the connector's `enqueuedTime` column to `enqueued_time` (the name used in the window aggregation) and enforces the JSON schema on the message body.

### Tumbling Window Aggregation

```python
windowed = parsed.withWatermark("enqueued_time", "2 minutes") \
    .groupBy(window("enqueued_time", "5 minutes"), "student_name") \
    .agg(count("*").alias("event_count"), avg("score").alias("avg_score"))
```

The windowed stream is written to ADLS Gen2 in Parquet format with a checkpoint location, so the stream can resume after a restart:

```python
windowed.writeStream \
    .format("parquet") \
    .outputMode("append") \
    .option("path", ADLS_OUTPUT_PATH) \
    .option("checkpointLocation", ADLS_CHECKPOINT_PATH) \
    .start()
```

Replace `<container>` in the ADLS paths in the notebook with the actual container name, and make sure storage authentication for `calablake141` is set up before starting the write stream.

## Screenshot Checklist

| # | Screenshot | Filename |
|---|---|---|
| 1 | Azure Portal — Event Hub Namespace overview | Step_01_EventHub_Namespace_Overview.png |
| 2 | Event Hub entity calab-eventhub-141 details | Step_02_EventHub_Entity_Details.png |
| 3 | SAS Policy DatabricksPolicy with keys | Step_03_SAS_Policy_Keys.png |
| 4 | Databricks Cluster with Maven library installed | Step_04_Cluster_Maven_Library.png |
| 5 | Producer script running — terminal output showing events sent | Step_05_Producer_Script_Running.png |
| 6 | Raw streaming events displayed in notebook | Step_06_Raw_Streaming_Events.png |
| 7 | Parsed JSON stream with student names and event types | Step_07_Parsed_JSON_Stream.png |
| 8 | Tumbling window aggregation — events per student | Step_08_Windowed_Aggregation.png |
| 9 | Event type distribution streaming chart | Step_09_Event_Type_Distribution.png |
| 10 | Streaming query status (active) | Step_10_Streaming_Query_Status.png |
| 11 | Output Parquet files in ADLS Gen2 | Step_11_Output_Parquet_ADLS.png |

Note: screenshots are not in this folder yet — add them under `screenshots/` using the filenames above. Do not include a screenshot that shows the full SAS connection string.

## Result

A live student-activity stream was ingested through Azure Event Hub, parsed and schema-enforced in Databricks Structured Streaming, aggregated into 5-minute tumbling windows per student (event count and average score), and written to ADLS Gen2 as Parquet files with checkpointing.

## Key Learning

This experiment demonstrates a complete real-time streaming pipeline on Azure: an event producer feeding Event Hub, a Spark Structured Streaming consumer that parses, validates and window-aggregates the stream, and a durable Parquet sink with checkpointing for fault-tolerant, resumable processing.
