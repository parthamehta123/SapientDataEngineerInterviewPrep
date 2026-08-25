terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }

  # Build all parent/child folder combinations for the source bucket
  folder_pairs = flatten([
    for parent in var.sample_parent_folders : [
      for child in var.sample_child_folders : {
        key = "${parent}/${child}/"
      }
    ]
  ])
}

# -----------------------------------------------------------------------------
# S3 Bucket — Source Data (where raw parquet/csv/json files land)
# -----------------------------------------------------------------------------
resource "aws_s3_bucket" "source" {
  bucket = var.source_bucket_name
  tags   = local.tags
}

resource "aws_s3_bucket_versioning" "source" {
  bucket = aws_s3_bucket.source.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "source" {
  bucket = aws_s3_bucket.source.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "source" {
  bucket                  = aws_s3_bucket.source.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Create the parent/child folder structure the ETL expects
resource "aws_s3_object" "source_folders" {
  for_each = { for fp in local.folder_pairs : fp.key => fp }

  bucket  = aws_s3_bucket.source.id
  key     = each.value.key
  content = ""
}

# -----------------------------------------------------------------------------
# S3 Bucket — Delta Lake storage (target tables written by Databricks)
# -----------------------------------------------------------------------------
resource "aws_s3_bucket" "delta" {
  bucket = var.delta_bucket_name
  tags   = local.tags
}

resource "aws_s3_bucket_versioning" "delta" {
  bucket = aws_s3_bucket.delta.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "delta" {
  bucket = aws_s3_bucket.delta.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "delta" {
  bucket                  = aws_s3_bucket.delta.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# -----------------------------------------------------------------------------
# IAM Role — Databricks cross-account access to both S3 buckets
# -----------------------------------------------------------------------------
resource "aws_iam_role" "databricks_s3_access" {
  name = "${var.project_name}-databricks-s3-role"
  tags = local.tags

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DatabricksAssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${var.databricks_aws_account_id}:root"
        }
        Action = "sts:AssumeRole"
        Condition = {
          StringEquals = {
            "sts:ExternalId" = var.databricks_workspace_org_id
          }
        }
      },
      {
        Sid    = "EC2AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "databricks_s3_access" {
  name = "${var.project_name}-databricks-s3-policy"
  role = aws_iam_role.databricks_s3_access.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ListBuckets"
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Resource = [
          aws_s3_bucket.source.arn,
          aws_s3_bucket.delta.arn
        ]
      },
      {
        Sid    = "ReadSourceBucket"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion"
        ]
        Resource = "${aws_s3_bucket.source.arn}/*"
      },
      {
        Sid    = "ReadWriteDeltaBucket"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.delta.arn}/*"
      }
    ]
  })
}

# -----------------------------------------------------------------------------
# Instance Profile — attach role to Databricks clusters
# -----------------------------------------------------------------------------
resource "aws_iam_instance_profile" "databricks" {
  name = "${var.project_name}-databricks-instance-profile"
  role = aws_iam_role.databricks_s3_access.name
  tags = local.tags
}
