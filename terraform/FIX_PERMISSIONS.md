# Fix IAM Permissions for AWS Deployment

## Problem
The `vittcott-user` lacks necessary permissions to create AWS resources.

**Current Permissions:**
- ✅ AmazonDynamoDBFullAccess
- ✅ AmazonS3FullAccess
- ✅ AmazonS3ReadOnlyAccess
- ✅ IAMReadOnlyAccess
- ❌ Missing: ECS, ECR, VPC, CloudWatch Logs, IAM write permissions, ALB, Secrets Manager

**Issue:** vittcott-user cannot attach policies to itself - you need root account or admin user.

---

## Solution - Use AWS Console (Recommended)

Since CLI doesn't have permissions, use the AWS Console:

### Step 1: Sign in to AWS Console
1. Go to https://console.aws.amazon.com/
2. Sign in with your **root account** or an **administrator user** (NOT vittcott-user)

### Step 2: Navigate to IAM
1. Search for "IAM" in the AWS search bar
2. Click on "IAM" service

### Step 3: Add Policies to vittcott-user
1. Click **"Users"** in the left sidebar
2. Click on **"vittcott-user"**
3. Go to the **"Permissions"** tab
4. Click **"Add permissions"** → **"Attach policies directly"**

### Step 4: Attach These 7 Policies
Search for and select each policy:

1. ✅ **AmazonECS_FullAccess** - For ECS cluster, services, task definitions
2. ✅ **AmazonEC2ContainerRegistryFullAccess** - For ECR repositories
3. ✅ **AmazonVPCFullAccess** - For VPC, subnets, NAT gateway, security groups
4. ✅ **CloudWatchLogsFullAccess** - For log groups and log streams
5. ✅ **IAMFullAccess** - For creating ECS task execution roles
6. ✅ **ElasticLoadBalancingFullAccess** - For Application Load Balancer
7. ✅ **SecretsManagerReadWrite** - For JWT and API key secrets

### Step 5: Verify
After adding, you should see **11 total policies** attached:
- Previous 4: DynamoDB, S3 Full, S3 ReadOnly, IAM ReadOnly
- New 7: ECS, ECR, VPC, CloudWatch Logs, IAM Full, ALB, Secrets Manager

---

## Verify Permissions (After Console Update)
Run this to confirm all policies are attached:

```powershell
aws iam list-attached-user-policies --user-name vittcott-user
```

---

## Alternative: CLI Commands (Requires Admin User)
If you have AWS credentials for an admin user, configure a new profile and use it:

```powershell
# Configure admin profile
aws configure --profile admin
# Then attach policies using the admin profile
aws iam attach-user-policy --user-name vittcott-user --policy-arn arn:aws:iam::aws:policy/AmazonECS_FullAccess --profile admin
aws iam attach-user-policy --user-name vittcott-user --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess --profile admin
aws iam attach-user-policy --user-name vittcott-user --policy-arn arn:aws:iam::aws:policy/AmazonVPCFullAccess --profile admin
aws iam attach-user-policy --user-name vittcott-user --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess --profile admin
aws iam attach-user-policy --user-name vittcott-user --policy-arn arn:aws:iam::aws:policy/IAMFullAccess --profile admin
aws iam attach-user-policy --user-name vittcott-user --policy-arn arn:aws:iam::aws:policy/ElasticLoadBalancingFullAccess --profile admin
aws iam attach-user-policy --user-name vittcott-user --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite --profile admin
```

---

## Next Steps After Fixing Permissions

### 1. Import Existing DynamoDB Table
Since Vittcott_Users already exists:
```powershell
cd e:\Vrishaangan\GitHub\vittcott_dynamodbtest\terraform
terraform import aws_dynamodb_table.users Vittcott_Users
```

### 2. Re-run Terraform Apply
```powershell
terraform apply -auto-approve
```

### 3. Push Docker Images to ECR
After Terraform creates ECR repositories:
```powershell
# Get ECR login
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 312871631203.dkr.ecr.ap-south-1.amazonaws.com

# Tag and push images
docker tag vittcott_dynamodbtest-node-backend:latest 312871631203.dkr.ecr.ap-south-1.amazonaws.com/vittcott-node-backend:latest
docker push 312871631203.dkr.ecr.ap-south-1.amazonaws.com/vittcott-node-backend:latest

docker tag vittcott_dynamodbtest-python-backend:latest 312871631203.dkr.ecr.ap-south-1.amazonaws.com/vittcott-python-backend:latest
docker push 312871631203.dkr.ecr.ap-south-1.amazonaws.com/vittcott-python-backend:latest

docker tag vittcott_dynamodbtest-streamlit:latest 312871631203.dkr.ecr.ap-south-1.amazonaws.com/vittcott-streamlit:latest
docker push 312871631203.dkr.ecr.ap-south-1.amazonaws.com/vittcott-streamlit:latest
```

### 4. Update ECS Services
```powershell
aws ecs update-service --cluster vittcott-cluster --service vittcott-node-backend --force-new-deployment --region ap-south-1
aws ecs update-service --cluster vittcott-cluster --service vittcott-python-backend --force-new-deployment --region ap-south-1
aws ecs update-service --cluster vittcott-cluster --service vittcott-streamlit --force-new-deployment --region ap-south-1
```

### 5. Get Application URL
```powershell
terraform output
# Look for alb_dns_name - that's your application URL
```
