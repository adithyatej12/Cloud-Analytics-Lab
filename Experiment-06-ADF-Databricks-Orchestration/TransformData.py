# Databricks notebook source
# Experiment 6: End-to-End Data Pipeline Orchestration
# using Azure Data Factory and Azure Databricks
#
# Run by: ADF pipeline PL_ADF_Databricks, activity RunTransformDataNotebook,
# after the Copy Data activity has copied student_performance.csv into
# the ADLS Gen2 rawdata container.
#
# Input : ADLS Gen2 rawdata/student_performance.csv
# Output: ADLS Gen2 output/student_performance_cleaned (Parquet)
#         ADLS Gen2 output/student_performance_cleaned_csv (CSV, one file)
#
# Storage authentication (mount / Spark configuration) for calablake141
# must already be set up before this notebook runs.
# Replace <container> only if your rawdata/output containers differ;
# the container names below are the ones used in this experiment.

# COMMAND ----------

from pyspark.sql.functions import col, when, lit
from pyspark.sql.types import NumericType

INPUT_PATH = "abfss://rawdata@calablake141.dfs.core.windows.net/student_performance.csv"
PARQUET_OUTPUT_PATH = "abfss://output@calablake141.dfs.core.windows.net/student_performance_cleaned"
CSV_OUTPUT_PATH = "abfss://output@calablake141.dfs.core.windows.net/student_performance_cleaned_csv"

# COMMAND ----------

# 1. Read the CSV copied into ADLS Gen2 by the ADF Copy Data activity.
df = spark.read.option("header", True).option("inferSchema", True).csv(INPUT_PATH)
print(f"Rows read: {df.count()}")
print(f"Columns: {df.columns}")
display(df.limit(20))

# COMMAND ----------

# 2. Data cleaning.
#    - Normalise column names (strip surrounding whitespace only;
#      original names are otherwise kept, so downstream code still matches).
#    - Trim whitespace in string values.
#    - Drop exact duplicate rows.
#    - Fill nulls: numeric columns with the column mean, string columns
#      with "Unknown". A column that is entirely null is filled with 0 /
#      "Unknown" respectively, so the mean step cannot introduce new nulls.
for old_name in df.columns:
    new_name = old_name.strip()
    if new_name != old_name:
        df = df.withColumnRenamed(old_name, new_name)

for field in df.schema.fields:
    if isinstance(field.dataType, NumericType):
        mean_value = df.select(field.name).na.drop().agg({field.name: "avg"}).first()[0]
        fill_value = mean_value if mean_value is not None else 0
        df = df.na.fill({field.name: fill_value})
    else:
        df = df.withColumn(field.name, col(field.name).cast("string"))
        df = df.na.fill({field.name: "Unknown"})

# Trim string values (Spark trim via regexp_replace-free approach:
# string columns are re-read trimmed by stripping in the next step only
# where a column is used in grouping; full trim is applied below).
from pyspark.sql.functions import trim

for field in df.schema.fields:
    if not isinstance(field.dataType, NumericType):
        df = df.withColumn(field.name, trim(col(field.name)))

rows_before_dedup = df.count()
df = df.dropDuplicates()
print(f"Rows before de-duplication: {rows_before_dedup}, after: {df.count()}")

# COMMAND ----------

# 3. Feature engineering.
#    Score-like columns are detected by name, so this step works for any
#    student_performance.csv layout that carries scores/marks/grades:
#    if such columns exist, average_score, total_score, performance_band
#    and result are added; if none exist, the cleaned data passes through
#    unchanged and the notebook reports that no score column was found.
score_cols = [
    field.name
    for field in df.schema.fields
    if isinstance(field.dataType, NumericType)
    and any(key in field.name.lower() for key in ("score", "marks", "grade"))
]

if score_cols:
    total_expr = sum(col(c) for c in score_cols)
    df = df.withColumn("total_score", total_expr)
    df = df.withColumn("average_score", total_expr / lit(len(score_cols)))
    df = df.withColumn(
        "performance_band",
        when(col("average_score") >= 85, "Excellent")
        .when(col("average_score") >= 70, "Good")
        .when(col("average_score") >= 50, "Average")
        .otherwise("Needs Improvement"),
    )
    df = df.withColumn(
        "result",
        when(col("average_score") >= 40, "Pass").otherwise("Fail"),
    )
    print(f"Score columns used: {score_cols}")
else:
    print("No score/marks/grade column found - cleaned data written without score features.")

display(df.limit(20))
print(f"Rows after cleaning: {df.count()}")

# COMMAND ----------

# 4. Validate and write the transformed output to ADLS Gen2.
#    Parquet is the primary output (verified in the experiment);
#    a single CSV copy is written alongside it for easy inspection.
assert df.count() > 0, "Transformed data is empty - check the input CSV in rawdata."

df.write.mode("overwrite").parquet(PARQUET_OUTPUT_PATH)
df.coalesce(1).write.mode("overwrite").option("header", True).csv(CSV_OUTPUT_PATH)

print(f"Parquet written to: {PARQUET_OUTPUT_PATH}")
print(f"CSV written to: {CSV_OUTPUT_PATH}")
