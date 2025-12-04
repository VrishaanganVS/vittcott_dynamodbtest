"""
CloudWatch Logger - Sends application logs to AWS CloudWatch
"""
import logging
import boto3
from datetime import datetime
from botocore.exceptions import ClientError
import os
import sys

class CloudWatchHandler(logging.Handler):
    """Custom logging handler that sends logs to AWS CloudWatch"""
    
    def __init__(self, log_group_name, log_stream_name, aws_region='ap-south-1'):
        super().__init__()
        self.log_group_name = log_group_name
        self.log_stream_name = log_stream_name
        self.aws_region = aws_region
        
        # Initialize CloudWatch Logs client
        self.client = boto3.client('logs', region_name=self.aws_region)
        
        # Create log group and stream if they don't exist
        self._setup_log_group_and_stream()
        
        # Sequence token for putting log events
        self.sequence_token = None
        
    def _setup_log_group_and_stream(self):
        """Create CloudWatch log group and stream if they don't exist"""
        try:
            # Create log group
            try:
                self.client.create_log_group(logGroupName=self.log_group_name)
                print(f"✅ Created CloudWatch log group: {self.log_group_name}")
            except self.client.exceptions.ResourceAlreadyExistsException:
                pass  # Log group already exists
            
            # Set retention policy (30 days)
            try:
                self.client.put_retention_policy(
                    logGroupName=self.log_group_name,
                    retentionInDays=30
                )
            except Exception as e:
                print(f"⚠️ Could not set retention policy: {e}")
            
            # Create log stream
            try:
                self.client.create_log_stream(
                    logGroupName=self.log_group_name,
                    logStreamName=self.log_stream_name
                )
                print(f"✅ Created CloudWatch log stream: {self.log_stream_name}")
            except self.client.exceptions.ResourceAlreadyExistsException:
                pass  # Log stream already exists
                
        except ClientError as e:
            print(f"❌ Error setting up CloudWatch logging: {e}")
            # Continue without CloudWatch if setup fails
    
    def emit(self, record):
        """Send log record to CloudWatch"""
        try:
            log_entry = {
                'timestamp': int(record.created * 1000),  # CloudWatch expects milliseconds
                'message': self.format(record)
            }
            
            # Prepare kwargs for put_log_events
            kwargs = {
                'logGroupName': self.log_group_name,
                'logStreamName': self.log_stream_name,
                'logEvents': [log_entry]
            }
            
            # Add sequence token if we have one
            if self.sequence_token:
                kwargs['sequenceToken'] = self.sequence_token
            
            # Send log to CloudWatch
            response = self.client.put_log_events(**kwargs)
            
            # Update sequence token for next call
            self.sequence_token = response.get('nextSequenceToken')
            
        except ClientError as e:
            # If sequence token is invalid, get the correct one and retry
            if e.response['Error']['Code'] == 'InvalidSequenceTokenException':
                expected_token = e.response['Error']['Message'].split('is: ')[-1]
                self.sequence_token = expected_token
                self.emit(record)  # Retry
            else:
                # Print error but don't crash the application
                print(f"⚠️ CloudWatch logging error: {e}", file=sys.stderr)
        except Exception as e:
            print(f"⚠️ Unexpected error in CloudWatch handler: {e}", file=sys.stderr)


def setup_cloudwatch_logging(
    log_group_name="/aws/vittcott/backend",
    log_stream_name=None,
    log_level=logging.INFO,
    enable_console=True
):
    """
    Configure CloudWatch logging for the application
    
    Args:
        log_group_name: CloudWatch log group name
        log_stream_name: CloudWatch log stream name (auto-generated if None)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_console: Also log to console
    
    Returns:
        Configured logger instance
    """
    # Auto-generate log stream name with timestamp if not provided
    if log_stream_name is None:
        timestamp = datetime.utcnow().strftime('%Y-%m-%d')
        hostname = os.environ.get('HOSTNAME', 'local')
        log_stream_name = f"{hostname}/{timestamp}"
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add CloudWatch handler if AWS credentials are available
    try:
        cloudwatch_handler = CloudWatchHandler(
            log_group_name=log_group_name,
            log_stream_name=log_stream_name,
            aws_region=os.getenv('AWS_REGION', 'ap-south-1')
        )
        cloudwatch_handler.setFormatter(formatter)
        logger.addHandler(cloudwatch_handler)
        print(f"✅ CloudWatch logging enabled: {log_group_name}/{log_stream_name}")
    except Exception as e:
        print(f"⚠️ CloudWatch logging disabled: {e}")
    
    # Add console handler if enabled
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_logger(name=None):
    """Get a logger instance"""
    return logging.getLogger(name)
