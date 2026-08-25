"""
Production batch ETL for existing S3 data on Databricks.

Use this when data already exists in S3 and you want a backfill/load job
instead of continuous streaming ingestion.

What this job does:
1. Scans the base S3 path for two-level folder structure (parent/child).
2. Skips empty child folders.
3. Reads mixed file formats (parquet/csv/json) from non-empty folders.
4. Filters files by modification timestamp (modified_after).
5. Adds ingestion metadata for lineage.
6. Applies optional data quality checks and writes invalid rows to quarantine.
7. Writes valid rows to Delta (append or upsert).
8. Optionally loads valid rows into Snowflake via Spark Snowflake connector.

Typical Databricks widget/env config:
- source_path:            s3://bucket/root/
- modified_after:         2026-08-20T00:00:00Z (optional)
- formats:                parquet,csv,json
- csv_header:             true|false
- csv_delimiter:          ,
- target_table:           analytics.bronze_events
- write_mode:             append|upsert
- primary_keys:           id,event_id (required when write_mode=upsert)
- event_time_col:         event_ts (optional)
- required_cols:          id,event_ts (optional)
- quarantine_table:       analytics.quarantine_events
- snowflake_enabled:      true|false
- sf_url:                 <account>.snowflakecomputing.com
- sf_user:                <user>
- sf_password:            <password>
- sf_database:            <db>
- sf_schema:              <schema>
- sf_warehouse:           <warehouse>
- sf_role:                <role>
- sf_table:               <db.schema.table>
"""

from __future__ import annotations

import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import reduce
from typing import Any, Dict, List, Optional

from delta.tables import DeltaTable
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import Window
from pyspark.sql import functions as F


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger("databricks-batch-etl")


@dataclass(frozen=True)
class JobConfig:
    source_path: str
    formats: List[str]
    modified_after: Optional[datetime]
    csv_header: bool
    csv_delimiter: str
    target_table: str
    write_mode: str
    primary_keys: List[str]
    event_time_col: str
    required_cols: List[str]
    quarantine_table: str
    snowflake_enabled: bool
    sf_options: Dict[str, str]
    sf_table: str


def get_dbutils(spark: SparkSession) -> Any:
    """Resolve dbutils in both notebook and Python script contexts."""
    try:
        return dbutils  # type: ignore[name-defined]
    except NameError:
        from pyspark.dbutils import DBUtils

        return DBUtils(spark)


def _read_param(name: str, default: str = "", dbutils_handle: Any = None) -> str:
    env_value = os.getenv(name.upper(), default)

    if dbutils_handle is None:
        return env_value

    try:
        value = dbutils_handle.widgets.get(name)
        return value if value else env_value
    except Exception:
        return env_value


def _parse_csv_list(raw: str) -> List[str]:
    return [v.strip() for v in raw.split(",") if v.strip()]


def _parse_bool(raw: str, default: bool = False) -> bool:
    if not raw:
        return default
    return raw.strip().lower() in {"1", "true", "t", "yes", "y"}


def _parse_iso_timestamp(raw: str) -> Optional[datetime]:
    if not raw:
        return None
    # Support a trailing Z by converting to UTC offset format.
    normalized = raw.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def load_config(dbutils_handle: Any = None) -> JobConfig:
    source_path = _read_param("source_path", "", dbutils_handle)
    formats = [f.lower() for f in _parse_csv_list(_read_param("formats", "parquet,csv,json", dbutils_handle))]
    modified_after = _parse_iso_timestamp(_read_param("modified_after", "", dbutils_handle))
    csv_header = _parse_bool(_read_param("csv_header", "true", dbutils_handle), default=True)
    csv_delimiter = _read_param("csv_delimiter", ",", dbutils_handle)
    target_table = _read_param("target_table", "", dbutils_handle)
    write_mode = _read_param("write_mode", "append", dbutils_handle).lower()
    primary_keys = _parse_csv_list(_read_param("primary_keys", "", dbutils_handle))
    event_time_col = _read_param("event_time_col", "", dbutils_handle)
    required_cols = _parse_csv_list(_read_param("required_cols", "", dbutils_handle))
    quarantine_table = _read_param("quarantine_table", "", dbutils_handle)

    snowflake_enabled = _parse_bool(_read_param("snowflake_enabled", "false", dbutils_handle), default=False)
    sf_table = _read_param("sf_table", "", dbutils_handle)
    sf_options = {
        "sfURL": _read_param("sf_url", "", dbutils_handle),
        "sfUser": _read_param("sf_user", "", dbutils_handle),
        "sfPassword": _read_param("sf_password", "", dbutils_handle),
        "sfDatabase": _read_param("sf_database", "", dbutils_handle),
        "sfSchema": _read_param("sf_schema", "", dbutils_handle),
        "sfWarehouse": _read_param("sf_warehouse", "", dbutils_handle),
        "sfRole": _read_param("sf_role", "", dbutils_handle),
    }

    if not source_path:
        raise ValueError("source_path is required")
    if not target_table:
        raise ValueError("target_table is required")
    if write_mode not in {"append", "upsert"}:
        raise ValueError("write_mode must be append or upsert")
    if write_mode == "upsert" and not primary_keys:
        raise ValueError("primary_keys is required when write_mode=upsert")

    allowed = {"parquet", "csv", "json"}
    invalid_formats = [f for f in formats if f not in allowed]
    if invalid_formats:
        raise ValueError(f"Unsupported formats: {invalid_formats}. Allowed: {sorted(allowed)}")

    if required_cols and not quarantine_table:
        raise ValueError("quarantine_table is required when required_cols are provided")

    if snowflake_enabled:
        missing_sf = [k for k, v in sf_options.items() if not v]
        if missing_sf:
            raise ValueError(f"Missing Snowflake options: {', '.join(missing_sf)}")
        if not sf_table:
            raise ValueError("sf_table is required when snowflake_enabled=true")

    return JobConfig(
        source_path=source_path,
        formats=formats,
        modified_after=modified_after,
        csv_header=csv_header,
        csv_delimiter=csv_delimiter,
        target_table=target_table,
        write_mode=write_mode,
        primary_keys=primary_keys,
        event_time_col=event_time_col,
        required_cols=required_cols,
        quarantine_table=quarantine_table,
        snowflake_enabled=snowflake_enabled,
        sf_options=sf_options,
        sf_table=sf_table,
    )


def _to_epoch_ms(ts: Optional[datetime]) -> Optional[int]:
    if ts is None:
        return None
    return int(ts.timestamp() * 1000)


def discover_candidate_files(cfg: JobConfig, dbutils_handle: Any) -> Dict[str, List[str]]:
    """
    Finds files in source_path/parent/child structure.
    Keeps only non-empty child folders and supported file extensions.
    """
    modified_after_ms = _to_epoch_ms(cfg.modified_after)
    grouped_paths: Dict[str, List[str]] = {fmt: [] for fmt in cfg.formats}

    parent_dirs = [x for x in dbutils_handle.fs.ls(cfg.source_path) if x.isDir()]
    logger.info("Found %s parent folders under %s", len(parent_dirs), cfg.source_path)

    for parent in parent_dirs:
        child_dirs = [x for x in dbutils_handle.fs.ls(parent.path) if x.isDir()]
        for child in child_dirs:
            files = [x for x in dbutils_handle.fs.ls(child.path) if not x.isDir()]
            if not files:
                logger.info("Skipping empty folder: %s", child.path)
                continue

            logger.info("Processing non-empty folder: %s (files=%s)", child.path, len(files))
            for f in files:
                ext = f.name.rsplit(".", 1)[-1].lower() if "." in f.name else ""
                if ext not in grouped_paths:
                    logger.warning("Unsupported format: %s (%s)", f.path, ext)
                    continue

                if modified_after_ms is not None and f.modificationTime <= modified_after_ms:
                    continue

                grouped_paths[ext].append(f.path)

    for fmt, paths in grouped_paths.items():
        logger.info("Discovered %s %s files for processing", len(paths), fmt)

    return grouped_paths


def _read_by_format(spark: SparkSession, fmt: str, paths: List[str], cfg: JobConfig) -> DataFrame:
    if fmt == "parquet":
        df = spark.read.format("parquet").load(paths)
    elif fmt == "json":
        df = spark.read.option("mode", "PERMISSIVE").format("json").load(paths)
    elif fmt == "csv":
        df = (
            spark.read.option("header", str(cfg.csv_header).lower())
            .option("delimiter", cfg.csv_delimiter)
            .option("mode", "PERMISSIVE")
            .format("csv")
            .load(paths)
        )
    else:
        raise ValueError(f"Unsupported format: {fmt}")

    run_id = str(uuid.uuid4())
    return (
        df.withColumn("_file_format", F.lit(fmt))
        .withColumn("_ingestion_ts", F.current_timestamp())
        .withColumn("_source_file", F.col("_metadata.file_path"))
        .withColumn("_run_id", F.lit(run_id))
    )


def read_and_union_files(spark: SparkSession, grouped_paths: Dict[str, List[str]], cfg: JobConfig) -> Optional[DataFrame]:
    dfs: List[DataFrame] = []

    for fmt, paths in grouped_paths.items():
        if not paths:
            continue
        dfs.append(_read_by_format(spark, fmt, paths, cfg))

    if not dfs:
        return None

    return reduce(lambda left, right: left.unionByName(right, allowMissingColumns=True), dfs)


def apply_quality_rules(df: DataFrame, cfg: JobConfig) -> tuple[DataFrame, DataFrame]:
    checked = df

    if cfg.event_time_col and cfg.event_time_col in checked.columns:
        checked = checked.withColumn(cfg.event_time_col, F.to_timestamp(F.col(cfg.event_time_col)))

    rule_expr = F.lit(None).cast("string")

    for key in cfg.primary_keys:
        if key not in checked.columns:
            raise ValueError(f"Primary key column not found: {key}")
        rule_expr = F.when(F.col(key).isNull(), F.lit(f"NULL_PRIMARY_KEY:{key}")).otherwise(rule_expr)

    for col_name in cfg.required_cols:
        if col_name not in checked.columns:
            raise ValueError(f"Required column not found: {col_name}")
        rule_expr = F.when(F.col(col_name).isNull(), F.lit(f"NULL_REQUIRED_COL:{col_name}")).otherwise(rule_expr)

    if cfg.event_time_col:
        if cfg.event_time_col not in checked.columns:
            raise ValueError(f"event_time_col not found: {cfg.event_time_col}")
        rule_expr = F.when(F.col(cfg.event_time_col).isNull(), F.lit("INVALID_EVENT_TIME")).otherwise(rule_expr)

    checked = checked.withColumn("_error_reason", rule_expr)
    valid_df = checked.filter(F.col("_error_reason").isNull()).drop("_error_reason")
    invalid_df = checked.filter(F.col("_error_reason").isNotNull())
    return valid_df, invalid_df


def write_quarantine(invalid_df: DataFrame, cfg: JobConfig) -> None:
    if invalid_df.rdd.isEmpty() or not cfg.quarantine_table:
        return

    (
        invalid_df.write.format("delta")
        .mode("append")
        .option("mergeSchema", "true")
        .saveAsTable(cfg.quarantine_table)
    )


def deduplicate(valid_df: DataFrame, cfg: JobConfig) -> DataFrame:
    if not cfg.primary_keys:
        return valid_df

    order_col = F.col("_ingestion_ts").desc()
    if cfg.event_time_col and cfg.event_time_col in valid_df.columns:
        order_col = F.col(cfg.event_time_col).desc_nulls_last()

    w = Window.partitionBy(*cfg.primary_keys).orderBy(order_col, F.col("_ingestion_ts").desc())
    return valid_df.withColumn("_rn", F.row_number().over(w)).filter(F.col("_rn") == 1).drop("_rn")


def write_to_delta(valid_df: DataFrame, cfg: JobConfig, spark: SparkSession) -> DataFrame:
    if valid_df.rdd.isEmpty():
        logger.info("No valid rows to write to Delta")
        return valid_df

    output_df = deduplicate(valid_df, cfg)

    if cfg.write_mode == "append":
        (
            output_df.write.format("delta")
            .mode("append")
            .option("mergeSchema", "true")
            .saveAsTable(cfg.target_table)
        )
        logger.info("Appended data to Delta table: %s", cfg.target_table)
        return output_df

    if not spark.catalog.tableExists(cfg.target_table):
        (
            output_df.write.format("delta")
            .mode("overwrite")
            .option("overwriteSchema", "true")
            .saveAsTable(cfg.target_table)
        )
        logger.info("Created Delta table and loaded data: %s", cfg.target_table)
        return output_df

    merge_condition = " AND ".join([f"t.{k} = s.{k}" for k in cfg.primary_keys])
    target = DeltaTable.forName(spark, cfg.target_table)

    (
        target.alias("t")
        .merge(output_df.alias("s"), merge_condition)
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )

    logger.info("Upserted data into Delta table: %s", cfg.target_table)
    return output_df


def write_to_snowflake(df: DataFrame, cfg: JobConfig) -> None:
    if not cfg.snowflake_enabled:
        return
    if df.rdd.isEmpty():
        logger.info("No valid rows to write to Snowflake")
        return

    (
        df.write.format("snowflake")
        .options(**cfg.sf_options)
        .option("dbtable", cfg.sf_table)
        .mode("append")
        .save()
    )
    logger.info("Loaded rows into Snowflake table: %s", cfg.sf_table)


def main() -> None:
    spark = SparkSession.getActiveSession() or SparkSession.builder.getOrCreate()
    dbutils_handle = get_dbutils(spark)
    cfg = load_config(dbutils_handle)

    logger.info("Starting batch ETL from %s", cfg.source_path)
    grouped_paths = discover_candidate_files(cfg, dbutils_handle)

    raw_df = read_and_union_files(spark, grouped_paths, cfg)
    if raw_df is None:
        logger.info("No files matched the discovery/filter criteria. Exiting.")
        return

    valid_df, invalid_df = apply_quality_rules(raw_df, cfg)
    write_quarantine(invalid_df, cfg)

    written_df = write_to_delta(valid_df, cfg, spark)
    write_to_snowflake(written_df, cfg)

    logger.info("Batch ETL completed successfully")


if __name__ == "__main__":
    main()
