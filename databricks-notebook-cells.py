# =============================================================================
# DATABRICKS NOTEBOOK — Paste these as two cells in your Databricks notebook
# =============================================================================

# ---- CELL 1: Configuration (set environment variables) ----------------------
# Attach this notebook to a cluster with the instance profile:
#   sapient-etl-databricks-instance-profile
#
# After terraform apply, replace the bucket name below with your actual bucket.

import os

os.environ["SOURCE_PATH"]       = "s3://sapient-etl-source-data-parthamehta/"
os.environ["MODIFIED_AFTER"]    = ""                          # e.g. "2026-08-20T00:00:00Z" or leave blank for all
os.environ["FORMATS"]           = "parquet,csv,json"
os.environ["CSV_HEADER"]        = "true"
os.environ["CSV_DELIMITER"]     = ","
os.environ["TARGET_TABLE"]      = "default.bronze_events"     # catalog.schema.table
os.environ["WRITE_MODE"]        = "append"                    # append | upsert
os.environ["PRIMARY_KEYS"]      = "id,event_id"              # required for upsert
os.environ["EVENT_TIME_COL"]    = "event_ts"
os.environ["REQUIRED_COLS"]     = "id,event_ts"
os.environ["QUARANTINE_TABLE"]  = "default.quarantine_events"
os.environ["SNOWFLAKE_ENABLED"] = "false"

print("Environment configured.")


# ---- CELL 2: Run the ETL script --------------------------------------------
# This executes 23-etl-question.py from the Git folder you cloned.

# %run /Workspace/Users/mehtapartha1@gmail.com/SapientDataEngineerInterviewPrep/23-etl-question
