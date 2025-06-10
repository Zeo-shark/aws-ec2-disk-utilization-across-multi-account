import json
import boto3
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
sns_client = boto3.client('sns')
cloudwatch = boto3.client('cloudwatch')

# Configuration
METRICS_TABLE = 'DiskUtilizationMetrics'
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
CRITICAL_THRESHOLD = int(os.environ.get('CRITICAL_THRESHOLD', '85'))
WARNING_THRESHOLD = int(os.environ.get('WARNING_THRESHOLD', '75'))

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for processing disk metrics from S3 events
    """
    try:
        # Process S3 event records
        for record in event.get('Records', []):
            if record['eventSource'] == 'aws:s3':
                process_s3_record(record)
                
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Successfully processed disk metrics',
                'timestamp': datetime.utcnow().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing metrics: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        }

def process_s3_record(record: Dict[str, Any]) -> None:
    """
    Process individual S3 record containing disk metrics
    """
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    
    logger.info(f"Processing S3 object: s3://{bucket}/{key}")
    
    try:
        # Parse account ID and timestamp from S3 key
        # Expected format: disk-metrics/{account_id}/{date}/{timestamp}.json
        key_parts = key.split('/')
        if len(key_parts) >= 4 and key_parts[0] == 'disk-metrics':
            account_id = key_parts[1]
            date = key_parts[2]
            timestamp = datetime.utcnow().isoformat()
            
            # Retrieve metrics data from S3
            metrics_data = get_s3_object_content(bucket, key)
            
            if metrics_data:
                # Process and aggregate metrics
                aggregated_metrics = aggregate_metrics(metrics_data, account_id, timestamp)
                
                # Store in DynamoDB
                store_aggregated_metrics(aggregated_metrics)
                
                # Send CloudWatch metrics
                send_cloudwatch_metrics(aggregated_metrics)
                
                # Check for alerts
                check_and_send_alerts(aggregated_metrics)
                
    except Exception as e:
        logger.error(f"Error processing S3 record {key}: {str(e)}")
        raise

def get_s3_object_content(bucket: str, key: str) -> List[Dict[str, Any]]:
    """
    Retrieve and parse JSON content from S3 object
    """
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
    except ClientError as e:
        logger.error(f"Error reading S3 object {bucket}/{key}: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON from {bucket}/{key}: {str(e)}")
        return []

def aggregate_metrics(metrics_data: List[Dict[str, Any]], account_id: str, timestamp: str) -> Dict[str, Any]:
    """
    Aggregate disk metrics for storage and analysis
    """
    if not metrics_data:
        return {}
    
    total_instances = len(metrics_data)
    high_usage_instances = []
    critical_instances = []
    utilization_sum = 0
    disk_count = 0
    
    for instance in metrics_data:
        instance_id = instance.get('instance_id', 'unknown')
        max_usage = 0
        
        for disk in instance.get('disks', []):
            usage_str = disk.get('usage', '0%').replace('%', '')
            try:
                usage = float(usage_str)
                utilization_sum += usage
                disk_count += 1
                max_usage = max(max_usage, usage)
            except ValueError:
                logger.warning(f"Invalid usage value: {usage_str}")
        
        # Track high usage instances
        if max_usage >= CRITICAL_THRESHOLD:
            critical_instances.append({
                'instance_id': instance_id,
                'max_usage': max_usage,
                'region': instance.get('region', 'unknown')
            })
        elif max_usage >= WARNING_THRESHOLD:
            high_usage_instances.append({
                'instance_id': instance_id,
                'max_usage': max_usage,
                'region': instance.get('region', 'unknown')
            })
    
    average_utilization = utilization_sum / disk_count if disk_count > 0 else 0
    
    return {
        'AccountId': account_id,
        'Timestamp': timestamp,
        'TotalInstances': total_instances,
        'TotalDisks': disk_count,
        'AverageUtilization': Decimal(str(round(average_utilization, 2))),
        'HighUsageInstances': high_usage_instances,
        'CriticalInstances': critical_instances,
        'HighUsageCount': len(high_usage_instances),
        'CriticalCount': len(critical_instances),
        'ProcessedAt': datetime.utcnow().isoformat()
    }

def store_aggregated_metrics(metrics: Dict[str, Any]) -> None:
    """
    Store aggregated metrics in DynamoDB
    """
    if not metrics:
        return
        
    try:
        table = dynamodb.Table(METRICS_TABLE)
        table.put_item(Item=metrics)
        logger.info(f"Stored metrics for account {metrics['AccountId']}")
    except ClientError as e:
        logger.error(f"Error storing metrics in DynamoDB: {str(e)}")
        raise

def send_cloudwatch_metrics(metrics: Dict[str, Any]) -> None:
    """
    Send custom metrics to CloudWatch
    """
    if not metrics:
        return
        
    try:
        metric_data = [
            {
                'MetricName': 'AverageUtilization',
                'Value': float(metrics.get('AverageUtilization', 0)),
                'Unit': 'Percent',
                'Dimensions': [
                    {
                        'Name': 'AccountId',
                        'Value': metrics['AccountId']
                    }
                ]
            },
            {
                'MetricName': 'CriticalInstances',
                'Value': metrics.get('CriticalCount', 0),
                'Unit': 'Count',
                'Dimensions': [
                    {
                        'Name': 'AccountId',
                        'Value': metrics['AccountId']
                    }
                ]
            },
            {
                'MetricName': 'TotalInstances',
                'Value': metrics.get('TotalInstances', 0),
                'Unit': 'Count',
                'Dimensions': [
                    {
                        'Name': 'AccountId',
                        'Value': metrics['AccountId']
                    }
                ]
            }
        ]
        
        cloudwatch.put_metric_data(
            Namespace='DiskMonitoring',
            MetricData=metric_data
        )
        
        logger.info(f"Sent CloudWatch metrics for account {metrics['AccountId']}")
        
    except ClientError as e:
        logger.error(f"Error sending CloudWatch metrics: {str(e)}")

def check_and_send_alerts(metrics: Dict[str, Any]) -> None:
    """
    Check metrics against thresholds and send alerts if necessary
    """
    critical_count = metrics.get('CriticalCount', 0)
    high_usage_count = metrics.get('HighUsageCount', 0)
    
    if critical_count > 0 or high_usage_count > 0:
        send_alert(metrics, critical_count, high_usage_count)

def send_alert(metrics: Dict[str, Any], critical_count: int, high_usage_count: int) -> None:
    """
    Send alert notification via SNS
    """
    if not SNS_TOPIC_ARN:
        logger.warning("SNS_TOPIC_ARN not configured, skipping alert")
        return
    
    try:
        account_id = metrics['AccountId']
        timestamp = metrics['Timestamp']
        
        message = {
            'alert_type': 'disk_utilization',
            'severity': 'critical' if critical_count > 0 else 'warning',
            'account_id': account_id,
            'timestamp': timestamp,
            'summary': {
                'critical_instances': critical_count,
                'high_usage_instances': high_usage_count,
                'total_instances': metrics.get('TotalInstances', 0)
            },
            'details': {
                'critical_instances': metrics.get('CriticalInstances', []),
                'high_usage_instances': metrics.get('HighUsageInstances', [])
            }
        }
        
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f"Disk Utilization Alert - Account {account_id}",
            Message=json.dumps(message, indent=2, default=str)
        )
        
        logger.info(f"Sent alert for account {account_id}: {critical_count} critical, {high_usage_count} warning")
        
    except ClientError as e:
        logger.error(f"Error sending SNS alert: {str(e)}")