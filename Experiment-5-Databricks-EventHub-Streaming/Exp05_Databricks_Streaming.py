# Databricks notebook source
# Experiment 5: Real-Time Streaming Data Processing using Databricks & Azure Event Hub
#
# Cluster: Single Node, Runtime 14.3 LTS, Standard_DS3_v2
# Maven library (install on the cluster first):
#   com.microsoft.azure:azure-eventhubs-spark_2.12:2.3.22
#
# Replace the connection-string placeholder below with the Primary
# Connection String of the DatabricksPolicy SAS policy. Do NOT commit
# a real connection string to GitHub.

# COMMAND ----------

from pyspark.sql.functions import col, from_json, window, count, avg
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

EVENT_HUB_CONNECTION_STRING = "<DatabricksPolicy primary connection string>"
EVENT_HUB_NAME = "calab-eventhub-141"

ehConf = {
    "eventhubs.connectionString": EVENT_HUB_CONNECTION_STRING,
    "eventhubs.eventHubName": EVENT_HUB_NAME,
    # Consumer group defaults to $Default when not specified.
}

# ADLS Gen2 sink — replace <container> with the actual container name.
# Storage authentication (mount / Spark configuration) must already be
# set up for calablake141 before this write stream is started.
ADLS_OUTPUT_PATH = (
    "abfss://<container>@calablake141.dfs.core.windows.net/output/streaming_events"
)
ADLS_CHECKPOINT_PATH = (
    "abfss://<container>@calablake141.dfs.core.windows.net/checkpoint/streaming_events"
)

# COMMAND ----------

# Schema enforcement for the JSON payload in the Event Hub message body.
# score is null for non-quiz events (see producer.py); avg() ignores nulls.
schema = StructType([
    StructField("student_name", StringType(), True),
    StructField("event_type", StringType(), True),
    StructField("score", IntegerType(), True),
    StructField("event_time", StringType(), True),
])

# COMMAND ----------

# Read the live stream from Event Hub with Structured Streaming.
raw_stream = spark.readStream.format("eventhubs").options(**ehConf).load()

# The connector exposes the enqueue timestamp as "enqueuedTime" and the
# message payload as binary "body". Alias the timestamp to the
# enqueued_time name used by the window aggregation below.
parsed = (
    raw_stream
    .withColumn("enqueued_time", col("enqueuedTime"))
    .select(
        col("enqueued_time"),
        from_json(col("body").cast("string"), schema).alias("event"),
    )
    .select("enqueued_time", "event.*")
)

# COMMAND ----------

# Raw / parsed stream as it arrives (Databricks display).
display(parsed)

# COMMAND ----------

# Tumbling window aggregation: 5-minute windows, 2-minute watermark
# for late events — event counts and average score per student.
windowed = (
    parsed
    .withWatermark("enqueued_time", "2 minutes")
    .groupBy(window("enqueued_time", "5 minutes"), "student_name")
    .agg(
        count("*").alias("event_count"),
        avg("score").alias("avg_score"),
    )
)

display(windowed)

# COMMAND ----------

# Event type distribution (streaming chart in the notebook).
event_type_counts = parsed.groupBy("event_type").count()

display(event_type_counts)

# COMMAND ----------

# Write the windowed output to ADLS Gen2 in Parquet format,
# with checkpointing so the stream can resume after a restart.
streaming_query = (
    windowed.writeStream
    .format("parquet")
    .outputMode("append")
    .option("path", ADLS_OUTPUT_PATH)
    .option("checkpointLocation", ADLS_CHECKPOINT_PATH)
    .start()
)

# Check that the query is active.
print(f"Streaming query active: {streaming_query.isActive}")
print(f"Query id: {streaming_query.id}")

# COMMAND ----------

# When finished: stop the stream, then terminate the cluster to save cost.
# streaming_query.stop()
