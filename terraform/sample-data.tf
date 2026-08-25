# -----------------------------------------------------------------------------
# Upload sample data files so the ETL has something to process immediately.
# These go into the parent/child structure the ETL's discover_candidate_files()
# scans for.
# -----------------------------------------------------------------------------

resource "aws_s3_object" "sample_parquet_placeholder" {
  bucket       = aws_s3_bucket.source.id
  key          = "events/2026-08-25/sample.parquet"
  source       = "${path.module}/../sample-data/sample.parquet"
  content_type = "application/octet-stream"

  # Only upload if the file exists locally; skip otherwise
  count = fileexists("${path.module}/../sample-data/sample.parquet") ? 1 : 0
}

resource "aws_s3_object" "sample_csv" {
  bucket       = aws_s3_bucket.source.id
  key          = "events/2026-08-25/sample.csv"
  content_type = "text/csv"

  content = <<-CSV
    id,event_id,event_ts,user_id,event_type,value
    1,evt-001,2026-08-25T10:00:00Z,user-101,click,1.5
    2,evt-002,2026-08-25T10:05:00Z,user-102,purchase,29.99
    3,evt-003,2026-08-25T10:10:00Z,user-103,view,0.0
    4,evt-004,2026-08-25T10:15:00Z,user-104,click,2.1
    5,evt-005,2026-08-25T10:20:00Z,user-105,purchase,49.99
  CSV
}

resource "aws_s3_object" "sample_json" {
  bucket       = aws_s3_bucket.source.id
  key          = "transactions/2026-08-25/sample.json"
  content_type = "application/json"

  content = <<-JSON
    {"id":1,"event_id":"txn-001","event_ts":"2026-08-25T11:00:00Z","user_id":"user-201","event_type":"transfer","value":100.00}
    {"id":2,"event_id":"txn-002","event_ts":"2026-08-25T11:05:00Z","user_id":"user-202","event_type":"deposit","value":500.00}
    {"id":3,"event_id":"txn-003","event_ts":"2026-08-25T11:10:00Z","user_id":"user-203","event_type":"withdrawal","value":75.50}
  JSON
}
