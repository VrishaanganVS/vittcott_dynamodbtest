# VittCott - Simplified Terraform Infrastructure

This is a **basic, simplified** Terraform configuration for the VittCott project. It creates only the essential AWS resources needed for local development.

## 📦 Resources Created

1. **DynamoDB Table** (`Vittcott_Users`)
   - User authentication data storage
   - Pay-per-request billing (no fixed costs)
   - Global Secondary Index on email

2. **S3 Bucket** (Portfolio Uploads)
   - File upload storage
   - Versioning enabled
   - CORS configured for local development

## 🚀 Quick Start

### Prerequisites
- AWS CLI configured with credentials
- Terraform installed (v1.0+)
- AWS account with basic permissions

### Setup

1. **Initialize Terraform**
   ```powershell
   cd terraform
   terraform init
   ```

2. **Review the Plan**
   ```powershell
   terraform plan
   ```

3. **Apply Configuration**
   ```powershell
   terraform apply
   ```

4. **Get Outputs**
   ```powershell
   terraform output
   ```

## 🔧 Configuration

### Variables (optional)
Create `terraform.tfvars`:
```hcl
aws_region = "ap-south-1"
environment = "dev"
project_name = "vittcott"
dynamodb_table_name = "Vittcott_Users"
```

## 🗑️ Cleanup

To destroy all resources:
```powershell
terraform destroy
```

## 📝 Notes

- **Cost**: Minimal costs with DynamoDB pay-per-request and S3 storage-only pricing
- **No Networking**: No VPC, ALB, NAT Gateway, or complex networking
- **Local Development**: Designed for running services locally (localhost:3000, :8000, :8501)
- **Simple**: Only creates DynamoDB table and S3 bucket

## ⚠️ Important

If the DynamoDB table already exists, you'll need to import it:
```powershell
terraform import aws_dynamodb_table.users Vittcott_Users
```

## 🔐 Required AWS Permissions

Minimal IAM permissions needed:
- `dynamodb:CreateTable`
- `dynamodb:DescribeTable`
- `dynamodb:TagResource`
- `s3:CreateBucket`
- `s3:PutBucketVersioning`
- `s3:PutBucketCORS`
- `s3:PutPublicAccessBlock`

