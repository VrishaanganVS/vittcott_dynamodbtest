terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Optional: Store state in S3 (uncomment for production)
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "vittcott/terraform.tfstate"
  #   region         = "ap-south-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-state-lock"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "VittCott"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
