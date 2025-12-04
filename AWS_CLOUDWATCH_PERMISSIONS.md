# 🔐 AWS IAM Permissions for CloudWatch Logging

## ⚠️ Issue: CloudWatch Access Denied

Your AWS user `vittcott-user` needs CloudWatch permissions to create log groups and send logs.

---

## ✅ Solution: Add IAM Policy

### Option 1: AWS Console (Easiest)

1. Go to: https://console.aws.amazon.com/iam/
2. Click **Users** → **vittcott-user**
3. Click **Add permissions** → **Attach policies directly**
4. Search for **CloudWatchLogsFullAccess**
5. Check the box and click **Next** → **Add permissions**

### Option 2: Use This Custom Policy (More Secure)

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
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogStreams",
        "logs:PutRetentionPolicy"
      ],
      "Resource": [
        "arn:aws:logs:ap-south-1:312871631203:log-group:/aws/vittcott/*",
        "arn:aws:logs:ap-south-1:312871631203:log-group:/aws/vittcott/*:log-stream:*"
      ]
    }
  ]
}
```

4. Click **Review policy**
5. Name it: `VittcottCloudWatchLogging`
6. Click **Create policy**

---

## 🧪 Test After Adding Permissions

```powershell
# Test CloudWatch logging
cd backend/src
python -c "from utils.cloudwatch_logger import setup_cloudwatch_logging; logger = setup_cloudwatch_logging(); logger.info('CloudWatch test successful!')"
```

You should see:
```
✅ Created CloudWatch log group: /aws/vittcott/backend
✅ Created CloudWatch log stream: local/2025-12-04
✅ CloudWatch logging enabled: /aws/vittcott/backend/local/2025-12-04
```

---

## 📊 Verify in AWS Console

After adding permissions:
1. Go to: https://console.aws.amazon.com/cloudwatch/
2. Click **Logs** → **Log groups**
3. You should see `/aws/vittcott/backend`
4. Click it to see your log streams

---

## ⚡ For Production: Create IAM Role

Instead of using IAM user credentials, use IAM roles:

1. Create EC2/Lambda/ECS role
2. Attach CloudWatch policy
3. No need to store AWS credentials
4. More secure!

---

**After adding permissions, your logs will stream automatically to CloudWatch! 🎉**
