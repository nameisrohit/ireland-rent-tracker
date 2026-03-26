resource "aws_s3_bucket" "raw_data" {
  bucket = "${var.project_name}-raw-data"

  tags = {
    Name      = "${var.project_name}-raw-data"
    Project   = var.project_name
    ManagedBy = "terraform"
  }
}

resource "aws_s3_bucket_public_access_block" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

output "s3_bucket_name" {
  description = "S3 data lake bucket name"
  value       = aws_s3_bucket.raw_data.bucket
}