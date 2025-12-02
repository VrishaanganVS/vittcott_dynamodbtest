variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "vittcott"
}

variable "dynamodb_table_name" {
  description = "DynamoDB table name for users"
  type        = string
  default     = "Vittcott_Users"
}
