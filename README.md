# Production ETL Pipeline — S3 to Delta Lake on Databricks

End-to-end batch ETL pipeline that ingests multi-format data (Parquet, CSV, JSON) from AWS S3 into Delta Lake tables on Databricks with data quality checks, lineage tracking, and optional Snowflake sink.

## Architecture

```
AWS S3 (source bucket)          Databricks (serverless)           Delta Lake
 events/2026-08-25/sample.csv    discover_candidate_files()        default.bronze_events
 transactions/2026-08-25/  ──>   read_and_union_files()      ──>   (valid rows)
   sample.json                   apply_quality_rules()
                                 deduplicate()                     default.quarantine_events
                                 write_to_delta()                  (invalid rows)
                                 write_to_snowflake() [optional]
```

## Features

- **Multi-format ingestion** — reads Parquet, CSV, and JSON files, unions them into a single DataFrame
- **Two-level folder scanning** — discovers files in `parent/child/` structure, skips empty folders
- **Modification-time filtering** — optional `modified_after` to process only new files
- **Data quality checks** — validates primary keys, required columns, and event timestamps; routes invalid rows to a quarantine table
- **Deduplication** — window-based dedup on primary keys using event time or ingestion timestamp
- **Delta Lake writes** — supports both `append` and `upsert` (MERGE) modes with schema evolution
- **Lineage metadata** — adds `_file_format`, `_ingestion_ts`, `_source_file`, `_run_id` to every row
- **Snowflake sink** — optional write to Snowflake via Spark connector

## Infrastructure (Terraform)

All AWS resources are managed via Terraform in the `terraform/` directory:

| Resource | Purpose |
|---|---|
| S3 bucket (source) | Raw data landing zone with parent/child folder structure |
| S3 bucket (delta) | Delta Lake table storage |
| IAM role + policy | Databricks cross-account S3 access (read source, read/write delta) |
| Instance profile | Attachable to Databricks clusters |
| Sample data | CSV and JSON files pre-loaded for immediate testing |

### Deploy

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Fill in your Databricks account details
terraform init && terraform apply
```

### Destroy (save costs)

```bash
terraform destroy
```

## Running the ETL on Databricks

1. Clone this repo as a Git folder in your Databricks workspace
2. Create a notebook and attach it to serverless compute
3. **Cell 1** — set environment variables:

```python
import os
os.environ["SOURCE_PATH"]       = "s3://your-source-bucket/"
os.environ["FORMATS"]           = "parquet,csv,json"
os.environ["CSV_HEADER"]        = "true"
os.environ["CSV_DELIMITER"]     = ","
os.environ["TARGET_TABLE"]      = "default.bronze_events"
os.environ["WRITE_MODE"]        = "append"
os.environ["PRIMARY_KEYS"]      = "id,event_id"
os.environ["EVENT_TIME_COL"]    = "event_ts"
os.environ["REQUIRED_COLS"]     = "id,event_ts"
os.environ["QUARANTINE_TABLE"]  = "default.quarantine_events"
os.environ["SNOWFLAKE_ENABLED"] = "false"
```

4. **Cell 2** — execute the ETL:

```python
exec(open("/Workspace/Users/<your-email>/production-etl-s3-to-delta/23-etl-question.py").read())
```

## Configuration Reference

| Parameter | Default | Description |
|---|---|---|
| `source_path` | *required* | S3 path to scan (e.g. `s3://bucket/root/`) |
| `formats` | `parquet,csv,json` | Comma-separated file formats to read |
| `modified_after` | *(none)* | ISO timestamp filter (e.g. `2026-08-20T00:00:00Z`) |
| `target_table` | *required* | Delta table name (e.g. `default.bronze_events`) |
| `write_mode` | `append` | `append` or `upsert` |
| `primary_keys` | *(none)* | Required for upsert mode |
| `event_time_col` | *(none)* | Column used for dedup ordering |
| `required_cols` | *(none)* | Columns that must be non-null |
| `quarantine_table` | *(none)* | Table for invalid rows |
| `snowflake_enabled` | `false` | Enable Snowflake sink |

## Tech Stack

Python, PySpark, Delta Lake, Databricks (Serverless), AWS S3, IAM, Terraform, Unity Catalog
