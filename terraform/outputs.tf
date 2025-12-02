# Outputs for the simplified infrastructure

output "dynamodb_table_name" {
  description = "Name of the DynamoDB users table"
  value       = aws_dynamodb_table.users.name
}

output "dynamodb_table_arn" {
  description = "ARN of the DynamoDB users table"
  value       = aws_dynamodb_table.users.arn
}

output "s3_bucket_name" {
  description = "Name of the S3 uploads bucket"
  value       = aws_s3_bucket.uploads.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 uploads bucket"
  value       = aws_s3_bucket.uploads.arn
}

output "aws_region" {
  description = "AWS region being used"
  value       = var.aws_region
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}
