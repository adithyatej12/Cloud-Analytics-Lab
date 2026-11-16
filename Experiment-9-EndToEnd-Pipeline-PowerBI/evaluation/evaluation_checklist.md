# Experiment 9 — Pipeline Evaluation Checklist

Fill this in from the actual evaluation run of pipeline `PL_ADF_Databricks` (Experiment 6 pipeline) and the Power BI visuals built on its curated output. Every observed value below is blank until the run happens — do not fill in numbers from memory or guesswork. Record what you actually observe, then judge each criterion Pass or Fail.

**Run details (fill in at evaluation time):**

- Date of run:
- Pipeline run ID:
- Triggered by:
- Power BI report name:

## Evaluation Criteria

| Criterion | What to measure | How to measure it | Observed value (to be filled from the run) | Pass/Fail |
|---|---|---|---|---|
| End-to-end latency | Total pipeline run duration, from trigger to both activities Succeeded | ADF Monitor → Pipeline Runs → run duration; also note each activity's duration (CopyRawDataToADLS, RunTransformDataNotebook) | | |
| Completeness — source | Row count of the source CSV (excluding the header) | Open `student_performance.csv` in Blob Storage and count data rows | | |
| Completeness — rawdata | Row count of the copied CSV in ADLS Gen2 `rawdata` | Open the copied file in `calablake141/rawdata` and count data rows; compare with the source count | | |
| Completeness — curated output | Row count of the cleaned Parquet in `output/student_performance_cleaned` | Read the Parquet output (notebook or query) and count rows; compare with the source and rawdata counts and account for any difference (e.g. duplicates dropped) | | |
| Data accuracy / quality — nulls | Whether nulls were handled as designed (numeric filled with column mean, strings with "Unknown") | Spot-check cleaned rows for remaining nulls; record sample size and findings | | |
| Data accuracy / quality — duplicates | Whether exact duplicate rows were removed | Check the cleaned output for surviving duplicate rows; record sample size and findings | | |
| Data accuracy / quality — derived columns | Whether `performance_band` and `result` are correct for each spot-checked row | Recompute by hand for the sampled rows: Excellent >= 85, Good >= 70, Average >= 50, otherwise Needs Improvement; Pass when average >= 40, otherwise Fail; record sample size and any mismatches | | |
| Freshness | Time from ingestion (pipeline trigger) to the finished Power BI visual | Note the trigger time (Step 3) and the time the visuals were complete (Step 10); record the elapsed time | | |
| Reliability | Both activities Succeeded; success dependency behaves as designed | ADF Monitor: confirm CopyRawDataToADLS and RunTransformDataNotebook both show Succeeded. Note: the success dependency means a failed copy never triggers a transform on stale or missing input — record what was observed for this run | | |
| Cost | Cost of the resources used by this run | Azure Cost Management — record the observed cost with the scope and period checked; do not estimate | | |
| Visualization correctness | Power BI totals match the Parquet aggregates | Compare Power BI totals (total students, count per performance_band, Pass/Fail split) with the aggregates from the Parquet output; record whether each matches | | |

## Notes

Use this space for anything the table does not capture: observations during the run, anything unexpected at a stage, and what would need fixing for any criterion marked Fail.

-
-
-

## Overall verdict

- Overall result (Pass / Fail):
- One-line summary of what the evaluation showed:
