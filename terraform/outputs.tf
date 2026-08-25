output "source_bucket_name" {
  description = "S3 bucket for raw source data"
  value       = aws_s3_bucket.source.id
}

output "source_bucket_arn" {
  value = aws_s3_bucket.source.arn
}

output "source_path_for_etl" {
  description = "Use this as source_path in the ETL job config"
  value       = "s3://${aws_s3_bucket.source.id}/"
}

output "delta_bucket_name" {
  description = "S3 bucket for Delta Lake tables"
  value       = aws_s3_bucket.delta.id
}

output "delta_bucket_arn" {
  value = aws_s3_bucket.delta.arn
}

output "databricks_iam_role_arn" {
  description = "IAM role ARN to configure in Databricks instance profile"
  value       = aws_iam_role.databricks_s3_access.arn
}

output "databricks_instance_profile_arn" {
  description = "Instance profile ARN to attach to Databricks clusters"
  value       = aws_iam_instance_profile.databricks.arn
}
