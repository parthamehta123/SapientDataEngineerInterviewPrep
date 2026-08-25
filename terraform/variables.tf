variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for naming resources"
  type        = string
  default     = "sapient-etl"
}

variable "environment" {
  description = "Environment tag (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "databricks_aws_account_id" {
  description = "Databricks control plane AWS account ID (414351767826 for US regions)"
  type        = string
  default     = "414351767826"
}

variable "databricks_workspace_org_id" {
  description = "Databricks workspace org ID (the 'o' param from your workspace URL)"
  type        = string
}

variable "databricks_workspace_url" {
  description = "Databricks workspace URL, e.g. https://dbc-xxxxx.cloud.databricks.com"
  type        = string
}

variable "source_bucket_name" {
  description = "S3 bucket name for raw source data"
  type        = string
  default     = "sapient-etl-source-data"
}

variable "delta_bucket_name" {
  description = "S3 bucket name for Delta Lake tables"
  type        = string
  default     = "sapient-etl-delta-lake"
}

variable "sample_parent_folders" {
  description = "Parent folders to create in source bucket (matching the ETL parent/child structure)"
  type        = list(string)
  default     = ["events", "transactions"]
}

variable "sample_child_folders" {
  description = "Child folders under each parent"
  type        = list(string)
  default     = ["2026-08-20", "2026-08-21", "2026-08-25"]
}
