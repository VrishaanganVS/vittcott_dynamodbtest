"""
AWS Integration Tests for Vittcott
Tests connectivity to AWS services (S3, DynamoDB)
"""
import boto3
import sys
import os
from botocore.exceptions import ClientError, NoCredentialsError

# Get AWS configuration from environment
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
S3_BUCKET = os.getenv("S3_PORTFOLIO_BUCKET", "vittcott-portfolios")
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE", "VittcottPortfolios")


class AWSTestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def test(self, name: str, test_func):
        """Run a single test"""
        print(f"\n{'='*60}")
        print(f"TEST: {name}")
        print(f"{'='*60}")
        try:
            result = test_func()
            if result:
                print(f"✅ PASSED: {name}")
                self.passed += 1
            else:
                print(f"❌ FAILED: {name}")
                self.failed += 1
        except Exception as e:
            print(f"❌ FAILED: {name}")
            print(f"   Error: {str(e)}")
            self.failed += 1
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*60}")
        print("AWS INTEGRATION TEST SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Passed:   {self.passed}")
        print(f"❌ Failed:   {self.failed}")
        print(f"⚠️  Warnings: {self.warnings}")
        print(f"{'='*60}\n")
        
        if self.failed > 0:
            print(f"❌ {self.failed} test(s) failed!")
            return False
        else:
            print("✅ All AWS integration tests passed!")
            return True


def test_aws_credentials(runner: AWSTestRunner):
    """Test AWS credentials are configured"""
    def run():
        try:
            sts = boto3.client('sts', region_name=AWS_REGION)
            response = sts.get_caller_identity()
            print(f"   AWS Account: {response['Account']}")
            print(f"   User ARN: {response['Arn']}")
            print(f"   User ID: {response['UserId']}")
            return True
        except NoCredentialsError:
            print(f"   ❌ No AWS credentials found")
            return False
        except Exception as e:
            print(f"   ❌ Credential check failed: {e}")
            return False
    
    runner.test("AWS Credentials", run)


def test_s3_bucket_access(runner: AWSTestRunner):
    """Test S3 bucket exists and is accessible"""
    def run():
        try:
            s3 = boto3.client('s3', region_name=AWS_REGION)
            
            # Check if bucket exists
            response = s3.head_bucket(Bucket=S3_BUCKET)
            print(f"   Bucket '{S3_BUCKET}' exists and is accessible")
            
            # Try to list objects (limited)
            list_response = s3.list_objects_v2(
                Bucket=S3_BUCKET,
                MaxKeys=5
            )
            
            object_count = list_response.get('KeyCount', 0)
            print(f"   Sample object count: {object_count}")
            
            if object_count > 0:
                print(f"   Sample objects:")
                for obj in list_response.get('Contents', [])[:3]:
                    print(f"      - {obj['Key']} ({obj['Size']} bytes)")
            
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"   ❌ Bucket '{S3_BUCKET}' not found")
            elif error_code == '403':
                print(f"   ❌ Access denied to bucket '{S3_BUCKET}'")
            else:
                print(f"   ❌ Error accessing bucket: {error_code}")
            return False
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            return False
    
    runner.test("S3 Bucket Access", run)


def test_s3_write_permission(runner: AWSTestRunner):
    """Test S3 write permissions with a test file"""
    def run():
        try:
            s3 = boto3.client('s3', region_name=AWS_REGION)
            
            test_key = 'test/aws-integration-test.txt'
            test_content = 'AWS integration test - this file can be deleted'
            
            # Try to put object
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=test_key,
                Body=test_content.encode('utf-8'),
                ContentType='text/plain'
            )
            print(f"   ✅ Successfully wrote test file: {test_key}")
            
            # Try to read it back
            response = s3.get_object(Bucket=S3_BUCKET, Key=test_key)
            content = response['Body'].read().decode('utf-8')
            assert content == test_content, "Read content doesn't match written content"
            print(f"   ✅ Successfully read test file back")
            
            # Clean up
            s3.delete_object(Bucket=S3_BUCKET, Key=test_key)
            print(f"   ✅ Test file deleted")
            
            return True
        except ClientError as e:
            print(f"   ❌ S3 write test failed: {e.response['Error']['Code']}")
            return False
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            return False
    
    runner.test("S3 Write Permissions", run)


def test_dynamodb_table_access(runner: AWSTestRunner):
    """Test DynamoDB table exists and is accessible"""
    def run():
        try:
            dynamodb = boto3.client('dynamodb', region_name=AWS_REGION)
            
            # Describe table
            response = dynamodb.describe_table(TableName=DYNAMODB_TABLE)
            
            table_status = response['Table']['TableStatus']
            item_count = response['Table']['ItemCount']
            
            print(f"   Table '{DYNAMODB_TABLE}' status: {table_status}")
            print(f"   Item count: {item_count}")
            print(f"   Table ARN: {response['Table']['TableArn']}")
            
            # Print key schema
            print(f"   Key Schema:")
            for key in response['Table']['KeySchema']:
                print(f"      - {key['AttributeName']} ({key['KeyType']})")
            
            assert table_status == 'ACTIVE', f"Table status is {table_status}, not ACTIVE"
            
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                print(f"   ❌ Table '{DYNAMODB_TABLE}' not found")
            elif error_code == 'AccessDeniedException':
                print(f"   ❌ Access denied to table '{DYNAMODB_TABLE}'")
            else:
                print(f"   ❌ Error accessing table: {error_code}")
            return False
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            return False
    
    runner.test("DynamoDB Table Access", run)


def test_dynamodb_read_write(runner: AWSTestRunner):
    """Test DynamoDB read/write operations"""
    def run():
        try:
            dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
            table = dynamodb.Table(DYNAMODB_TABLE)
            
            test_item = {
                'userId': 'test-aws-integration',
                'timestamp': '2025-01-01T00:00:00Z',
                'testData': 'This is a test item for AWS integration testing'
            }
            
            # Put item
            table.put_item(Item=test_item)
            print(f"   ✅ Successfully wrote test item")
            
            # Get item
            response = table.get_item(
                Key={'userId': 'test-aws-integration'}
            )
            
            assert 'Item' in response, "Failed to retrieve test item"
            assert response['Item']['testData'] == test_item['testData'], "Retrieved data doesn't match"
            print(f"   ✅ Successfully read test item back")
            
            # Delete item
            table.delete_item(
                Key={'userId': 'test-aws-integration'}
            )
            print(f"   ✅ Test item deleted")
            
            return True
        except ClientError as e:
            print(f"   ❌ DynamoDB operation failed: {e.response['Error']['Code']}")
            return False
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            return False
    
    runner.test("DynamoDB Read/Write Operations", run)


def test_aws_region_configuration(runner: AWSTestRunner):
    """Test AWS region is correctly configured"""
    def run():
        session = boto3.session.Session()
        current_region = session.region_name or os.getenv('AWS_DEFAULT_REGION', 'Not set')
        
        print(f"   Configured region: {AWS_REGION}")
        print(f"   Session region: {current_region}")
        
        if AWS_REGION == current_region or current_region == 'Not set':
            print(f"   ✅ Region configuration is correct")
            return True
        else:
            print(f"   ⚠️  Region mismatch detected")
            runner.warnings += 1
            return True
    
    runner.test("AWS Region Configuration", run)


def main():
    """Run all AWS integration tests"""
    print(f"\n{'#'*60}")
    print(f"# AWS INTEGRATION TESTS")
    print(f"# Region: {AWS_REGION}")
    print(f"# S3 Bucket: {S3_BUCKET}")
    print(f"# DynamoDB Table: {DYNAMODB_TABLE}")
    print(f"{'#'*60}\n")
    
    runner = AWSTestRunner()
    
    # Run all tests
    test_aws_credentials(runner)
    test_s3_bucket_access(runner)
    test_s3_write_permission(runner)
    test_dynamodb_table_access(runner)
    test_dynamodb_read_write(runner)
    test_aws_region_configuration(runner)
    
    # Print summary
    success = runner.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
