# 🚀 AWS Elastic Beanstalk Deployment - Permissions Needed

## ⚠️ Issue: Elastic Beanstalk Access Denied

Your AWS user `vittcott-user` needs Elastic Beanstalk permissions to deploy.

---

## ✅ Solution: Add IAM Policy

### Option 1: AWS Console (Quick - 2 minutes)

1. Go to: https://console.aws.amazon.com/iam/home?region=ap-south-1#/users/vittcott-user
2. Click **Add permissions** → **Attach policies directly**
3. Search for and check these policies:
   - ✅ **AWSElasticBeanstalkFullAccess**
   - ✅ **AWSElasticBeanstalkManagedUpdatesCustomerRolePolicy**
4. Click **Next** → **Add permissions**

### Option 2: Custom Policy (More Secure)

1. Go to IAM Console → Users → vittcott-user
2. Click **Add permissions** → **Create inline policy**
3. Click **JSON** tab and paste:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "elasticbeanstalk:*",
        "ec2:*",
        "elasticloadbalancing:*",
        "autoscaling:*",
        "cloudwatch:*",
        "s3:*",
        "sns:*",
        "cloudformation:*",
        "rds:*",
        "iam:GetRole",
        "iam:CreateRole",
        "iam:PutRolePolicy",
        "iam:PassRole",
        "iam:CreateInstanceProfile",
        "iam:AddRoleToInstanceProfile"
      ],
      "Resource": "*"
    }
  ]
}
```

4. Name it: `VittcottElasticBeanstalkDeploy`
5. Click **Create policy**

---

## 🎯 What These Permissions Allow

- **Elastic Beanstalk**: Create and manage applications
- **EC2**: Launch instances for your app
- **Load Balancer**: Distribute traffic
- **Auto Scaling**: Scale up/down based on load
- **CloudWatch**: Monitor and log
- **S3**: Store application versions
- **IAM**: Create service roles

---

## 🧪 After Adding Permissions

Run this command again:
```powershell
cd backend
eb init -p python-3.11 vittcott-backend --region ap-south-1
```

---

## 📋 Full Deployment Steps (After Permissions)

I'll handle these automatically once you add permissions:

1. ✅ Initialize EB application
2. ✅ Create environment
3. ✅ Upload code to S3
4. ✅ Launch EC2 instances
5. ✅ Configure load balancer
6. ✅ Set environment variables
7. ✅ Enable CloudWatch logging
8. ✅ Test deployment

---

**Add the permissions and I'll continue the deployment! 🚀**
