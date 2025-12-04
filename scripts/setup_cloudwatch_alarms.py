"""
CloudWatch Alarms Setup - Automatically create alarms for critical metrics
"""
import boto3
from botocore.exceptions import ClientError

def create_cloudwatch_alarms():
    """Create CloudWatch alarms for monitoring application health"""
    
    cloudwatch = boto3.client('cloudwatch', region_name='ap-south-1')
    sns = boto3.client('sns', region_name='ap-south-1')
    
    # Create SNS topic for notifications (optional)
    topic_arn = None
    try:
        response = sns.create_topic(Name='VittcottAlerts')
        topic_arn = response['TopicArn']
        print(f"✅ Created SNS topic: {topic_arn}")
        print("   Subscribe your email at: https://console.aws.amazon.com/sns/")
    except ClientError as e:
        print(f"⚠️ SNS topic creation skipped: {e}")
    
    alarms_created = []
    
    # Alarm 1: High Error Rate
    try:
        cloudwatch.put_metric_alarm(
            AlarmName='Vittcott-HighErrorRate',
            ComparisonOperator='GreaterThanThreshold',
            EvaluationPeriods=1,
            MetricName='Errors',
            Namespace='AWS/Logs',
            Period=300,  # 5 minutes
            Statistic='Sum',
            Threshold=10.0,
            ActionsEnabled=True if topic_arn else False,
            AlarmActions=[topic_arn] if topic_arn else [],
            AlarmDescription='Alert when error count exceeds 10 in 5 minutes',
            Dimensions=[
                {
                    'Name': 'LogGroupName',
                    'Value': '/aws/vittcott/backend'
                }
            ]
        )
        alarms_created.append('Vittcott-HighErrorRate')
        print("✅ Created alarm: Vittcott-HighErrorRate")
    except ClientError as e:
        print(f"⚠️ Error creating HighErrorRate alarm: {e}")
    
    # Alarm 2: Application Down (No Logs)
    try:
        cloudwatch.put_metric_alarm(
            AlarmName='Vittcott-ApplicationDown',
            ComparisonOperator='LessThanThreshold',
            EvaluationPeriods=2,
            MetricName='IncomingLogEvents',
            Namespace='AWS/Logs',
            Period=300,
            Statistic='Sum',
            Threshold=1.0,
            ActionsEnabled=True if topic_arn else False,
            AlarmActions=[topic_arn] if topic_arn else [],
            AlarmDescription='Alert when no logs received for 10 minutes',
            Dimensions=[
                {
                    'Name': 'LogGroupName',
                    'Value': '/aws/vittcott/backend'
                }
            ]
        )
        alarms_created.append('Vittcott-ApplicationDown')
        print("✅ Created alarm: Vittcott-ApplicationDown")
    except ClientError as e:
        print(f"⚠️ Error creating ApplicationDown alarm: {e}")
    
    # Create Metric Filter for Error Counting
    logs = boto3.client('logs', region_name='ap-south-1')
    try:
        logs.put_metric_filter(
            logGroupName='/aws/vittcott/backend',
            filterName='ErrorCount',
            filterPattern='[timestamp, request_id, level = ERROR*, ...]',
            metricTransformations=[
                {
                    'metricName': 'ErrorCount',
                    'metricNamespace': 'Vittcott/Application',
                    'metricValue': '1',
                    'defaultValue': 0
                }
            ]
        )
        print("✅ Created metric filter: ErrorCount")
    except ClientError as e:
        print(f"⚠️ Error creating metric filter: {e}")
    
    # Alarm 3: High Error Count (using custom metric)
    try:
        cloudwatch.put_metric_alarm(
            AlarmName='Vittcott-CustomErrorCount',
            ComparisonOperator='GreaterThanThreshold',
            EvaluationPeriods=1,
            MetricName='ErrorCount',
            Namespace='Vittcott/Application',
            Period=300,
            Statistic='Sum',
            Threshold=5.0,
            ActionsEnabled=True if topic_arn else False,
            AlarmActions=[topic_arn] if topic_arn else [],
            AlarmDescription='Alert when error count exceeds 5 in 5 minutes',
            TreatMissingData='notBreaching'
        )
        alarms_created.append('Vittcott-CustomErrorCount')
        print("✅ Created alarm: Vittcott-CustomErrorCount")
    except ClientError as e:
        print(f"⚠️ Error creating CustomErrorCount alarm: {e}")
    
    print(f"\n🎉 Created {len(alarms_created)} CloudWatch alarms!")
    print("\n📊 View your alarms at:")
    print("   https://console.aws.amazon.com/cloudwatch/home?region=ap-south-1#alarmsV2:")
    
    if topic_arn:
        print(f"\n📧 To receive email alerts:")
        print(f"   1. Go to: https://console.aws.amazon.com/sns/")
        print(f"   2. Click on topic: VittcottAlerts")
        print(f"   3. Click 'Create subscription'")
        print(f"   4. Protocol: Email, Endpoint: your@email.com")
    
    return alarms_created

if __name__ == "__main__":
    print("🚨 Setting up CloudWatch Alarms...\n")
    create_cloudwatch_alarms()
