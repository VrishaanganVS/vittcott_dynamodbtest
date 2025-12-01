# VittCott Terraform Infrastructure

This directory contains Terraform configuration for deploying VittCott to AWS ECS Fargate.

## Architecture

- **VPC**: Custom VPC with public and private subnets across 2 AZs
- **ECS Fargate**: Serverless container orchestration for 3 services
- **Application Load Balancer**: Routes traffic to services
- **DynamoDB**: User data storage with GSI
- **ECR**: Docker image registry
- **Secrets Manager**: Secure storage for API keys
- **IAM**: Roles and policies for service access
- **CloudWatch**: Logging and monitoring

## Prerequisites

1. **AWS CLI** configured with credentials
2. **Terraform** installed (v1.0+)
3. **Docker images** built and ready to push to ECR

## Setup

### 1. Configure Variables

```powershell
# Copy example file
Copy-Item terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
notepad terraform.tfvars
```

Required variables:
- `jwt_secret` - Your JWT secret key
- `gemini_api_key` - Your Gemini API key

### 2. Initialize Terraform

```powershell
cd terraform
terraform init
```

### 3. Plan Deployment

```powershell
terraform plan
```

### 4. Deploy Infrastructure

```powershell
terraform apply
```

Type `yes` when prompted.

## Post-Deployment Steps

### 1. Push Docker Images to ECR

```powershell
# Get ECR login
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-south-1.amazonaws.com

# Tag and push images
docker tag vittcott-node:latest <node-ecr-url>:latest
docker push <node-ecr-url>:latest

docker tag vittcott-python:latest <python-ecr-url>:latest
docker push <python-ecr-url>:latest

docker tag vittcott-streamlit:latest <streamlit-ecr-url>:latest
docker push <streamlit-ecr-url>:latest
```

### 2. Update ECS Services

After pushing images, force new deployment:

```powershell
aws ecs update-service --cluster vittcott-cluster --service vittcott-node-backend --force-new-deployment
aws ecs update-service --cluster vittcott-cluster --service vittcott-python-backend --force-new-deployment
aws ecs update-service --cluster vittcott-cluster --service vittcott-streamlit --force-new-deployment
```

### 3. Access Application

Get ALB DNS name:

```powershell
terraform output alb_dns_name
```

Access your services:
- Node Backend: `http://<alb-dns>:3000`
- Python Backend: `http://<alb-dns>:8000`
- Streamlit: `http://<alb-dns>:8501`

## Managing Infrastructure

### View Outputs

```powershell
terraform output
```

### Update Infrastructure

```powershell
# After modifying .tf files
terraform plan
terraform apply
```

### Destroy Infrastructure

```powershell
terraform destroy
```

⚠️ **Warning**: This will delete ALL resources including DynamoDB data!

## Cost Estimate

Approximate monthly costs (us-east-1):
- **ECS Fargate**: ~$30-50 (3 tasks running 24/7)
- **Application Load Balancer**: ~$20
- **NAT Gateway**: ~$35
- **DynamoDB**: ~$1-5 (on-demand, depends on usage)
- **CloudWatch Logs**: ~$1-2
- **ECR**: ~$1 (first 50GB free)

**Total**: ~$88-113/month

### Cost Optimization Tips

1. **Use Fargate Spot** for non-critical workloads
2. **Scale down** during off-hours (set desired_count = 0)
3. **Use provisioned DynamoDB** if predictable traffic
4. **Enable VPC endpoints** to avoid NAT Gateway costs
5. **Set log retention** to 7 days (already configured)

## Troubleshooting

### Task Won't Start

```powershell
# Check task status
aws ecs describe-tasks --cluster vittcott-cluster --tasks <task-id>

# View logs
aws logs tail /ecs/vittcott/node-backend --follow
```

### Health Check Failing

- Verify container ports match task definition
- Check security group rules
- Review application logs in CloudWatch

### Can't Access ALB

- Ensure security group allows port 80
- Verify target health in EC2 console
- Check ECS service is running

## Security Notes

- Never commit `terraform.tfvars` with secrets
- Use AWS Secrets Manager for sensitive data
- Rotate JWT secret regularly
- Enable VPC Flow Logs for production
- Add WAF rules to ALB for production

## Next Steps

1. Set up CI/CD pipeline (GitHub Actions)
2. Add auto-scaling policies
3. Configure custom domain with Route53
4. Add SSL/TLS certificate
5. Implement backup strategy
6. Set up monitoring alerts
