# 📊 CloudWatch Logging Setup Guide

## ✅ What I've Configured

### 1. **CloudWatch Logger** (`backend/src/utils/cloudwatch_logger.py`)
- Automatically sends all application logs to AWS CloudWatch
- Creates log groups and streams automatically
- 30-day log retention policy
- Fallback to console if CloudWatch unavailable

### 2. **Application Integration** (`backend/src/main.py`)
- CloudWatch logging initialized on startup
- Request/response logging middleware
- Tracks all API calls with:
  - Request ID
  - HTTP method and path
  - Response status
  - Duration
  - Errors with stack traces

---

## 🚀 How It Works

### Automatic Log Streaming
Every time your backend runs:
1. Logs are sent to CloudWatch: `/aws/vittcott/backend`
2. Log streams created per day: `hostname/YYYY-MM-DD`
3. All levels logged: INFO, WARNING, ERROR, CRITICAL

### What Gets Logged
- ✅ Application startup/shutdown
- ✅ All HTTP requests (method, path, client IP)
- ✅ Response status codes and durations
- ✅ Errors with full stack traces
- ✅ Database operations
- ✅ AI model interactions
- ✅ Portfolio analysis events

---

## 📖 View Logs in AWS Console

### Method 1: AWS Console
1. Go to: https://console.aws.amazon.com/cloudwatch/
2. Click **Logs** → **Log groups**
3. Find `/aws/vittcott/backend`
4. Click on a log stream to view logs

### Method 2: AWS CLI
```bash
# View latest logs
aws logs tail /aws/vittcott/backend --follow --region ap-south-1

# Search logs for errors
aws logs filter-log-events \
  --log-group-name /aws/vittcott/backend \
  --filter-pattern "ERROR" \
  --region ap-south-1

# Get logs from last hour
aws logs filter-log-events \
  --log-group-name /aws/vittcott/backend \
  --start-time $(date -u -d '1 hour ago' +%s)000 \
  --region ap-south-1
```

### Method 3: CloudWatch Insights
```sql
-- Find all errors in last 24 hours
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100

-- API response time analysis
fields @timestamp, @message
| filter @message like /Duration/
| parse @message /Duration: (?<duration>\d+\.\d+)s/
| stats avg(duration), max(duration), min(duration)

-- Most called endpoints
fields @timestamp, @message
| filter @message like /GET|POST|PUT|DELETE/
| parse @message /(?<method>\w+) (?<path>\/\S+)/
| stats count() by path
| sort count() desc
```

---

## 🔧 Testing CloudWatch Logging

### Test Locally
```powershell
# Start backend (CloudWatch will be enabled)
cd backend
python -m uvicorn src.main:app --reload --port 8000

# Make some requests
curl http://localhost:8000/api
curl http://localhost:8000/api/stocks/live

# Check logs in AWS Console
```

### Verify Logs Are Streaming
1. Open CloudWatch Console
2. Navigate to Log groups → `/aws/vittcott/backend`
3. You should see new log streams appear
4. Click on stream to see real-time logs

---

## 🎯 Log Levels

Configure via environment variable:
```bash
# .env file
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

**Recommended by environment:**
- **Development:** `DEBUG` (verbose, all details)
- **Staging:** `INFO` (standard operation logs)
- **Production:** `WARNING` (only warnings and errors)

---

## 📊 CloudWatch Metrics & Alarms

### Create Alarms for Critical Events

#### 1. Error Rate Alarm
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name vittcott-high-error-rate \
  --alarm-description "Alert when error rate is high" \
  --metric-name ErrorCount \
  --namespace AWS/Logs \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1
```

#### 2. API Latency Alarm
Monitor slow API responses using CloudWatch Insights.

---

## 💰 Cost Optimization

### Current Setup (Free Tier Friendly)
- **Log ingestion:** First 5GB/month FREE
- **Log storage:** First 5GB/month FREE
- **Retention:** 30 days (configurable)

### Reduce Costs
1. **Filter sensitive logs** - Don't log everything
2. **Adjust retention** - Lower to 7 days if needed
3. **Use log sampling** - Log 10% of successful requests

### Modify Retention
```python
# In cloudwatch_logger.py, change:
retentionInDays=30  # Change to 7, 14, or 30
```

---

## 🔍 Advanced: Structured Logging

For better searchability, use structured JSON logs:

```python
# Example in your code
logger.info("Portfolio analyzed", extra={
    "user_id": "vaibhav",
    "portfolio_value": 41750,
    "profit_loss": 3050,
    "num_holdings": 2
})
```

Then query in CloudWatch Insights:
```sql
fields @timestamp, user_id, portfolio_value, profit_loss
| filter user_id = "vaibhav"
| sort @timestamp desc
```

---

## 🚨 Error Tracking

All errors are automatically logged with full stack traces:

```python
# Example error log format
2025-12-04 10:30:45 - ERROR - [abc123] POST /api/portfolio/analyze - ERROR: Division by zero
Traceback (most recent call last):
  File "portfolio_service.py", line 45, in analyze
    return total / count
ZeroDivisionError: division by zero
```

---

## 📱 Integration with Slack/Email

Set up CloudWatch Alarms to notify you:

1. Create SNS topic
2. Subscribe email/Slack
3. Configure alarm to publish to SNS
4. Get notified on errors!

---

## ✅ Next Steps

1. **Start your backend** - CloudWatch logging is automatic
2. **Make some requests** - Generate logs
3. **Check AWS Console** - View logs in real-time
4. **Set up alarms** - Get notified of issues
5. **Create dashboards** - Visualize metrics

---

## 🐛 Troubleshooting

### "Unable to create log group"
**Solution:** Check AWS credentials have CloudWatch permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogStreams"
    ],
    "Resource": "arn:aws:logs:*:*:*"
  }]
}
```

### "Logs not appearing"
1. Check AWS region matches: `ap-south-1`
2. Verify AWS credentials in `.env`
3. Check console output for errors

### "Too expensive"
1. Reduce log level to WARNING
2. Lower retention to 7 days
3. Filter out health check logs

---

**Your logs are now streaming to CloudWatch! 🎉**

Check: https://console.aws.amazon.com/cloudwatch/home?region=ap-south-1#logsV2:log-groups/log-group/$252Faws$252Fvittcott$252Fbackend
