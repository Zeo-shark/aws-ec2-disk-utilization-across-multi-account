#!/usr/bin/env python3

import boto3
import json
import os
from datetime import datetime, timedelta

def create_cloudwatch_dashboard(account_id, region):
    cloudwatch = boto3.client('cloudwatch', region_name=region)
    
    # Create dashboard JSON
    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["EC2/DiskUtilization", "DiskUsagePercent", "InstanceId", "*", "MountPoint", "*"],
                        [".", "AvailableDiskSpace", ".", ".", ".", "."]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": region,
                    "title": "Disk Utilization Across All Instances",
                    "period": 300
                }
            },
            {
                "type": "metric",
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["EC2/DiskUtilization", "DiskUsagePercent", "InstanceId", "*"],
                        [".", "AvailableDiskSpace", ".", "."]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": region,
                    "title": "Aggregated Disk Metrics",
                    "period": 300
                }
            }
        ]
    }
    
    try:
        cloudwatch.put_dashboard(
            DashboardName=f"DiskUtilization-{account_id}",
            DashboardBody=json.dumps(dashboard_body)
        )
        print(f"Created dashboard for account {account_id} in region {region}")
    except Exception as e:
        print(f"Error creating dashboard: {str(e)}")

def create_cloudwatch_alarms(account_id, region):
    cloudwatch = boto3.client('cloudwatch', region_name=region)
    
    # Create alarm for high disk usage
    try:
        cloudwatch.put_metric_alarm(
            AlarmName=f"HighDiskUsage-{account_id}",
            AlarmDescription="Alarm when disk usage exceeds 80%",
            MetricName="DiskUsagePercent",
            Namespace="EC2/DiskUtilization",
            Statistic="Maximum",
            Period=300,
            EvaluationPeriods=2,
            Threshold=80.0,
            ComparisonOperator="GreaterThanThreshold",
            TreatMissingData="missing",
            Dimensions=[
                {
                    "Name": "InstanceId",
                    "Value": "*"
                }
            ],
            AlarmActions=[
                f"arn:aws:sns:{region}:{account_id}:DiskUtilizationAlerts"
            ]
        )
        print(f"Created high disk usage alarm for account {account_id}")
    except Exception as e:
        print(f"Error creating high disk usage alarm: {str(e)}")
    
    # Create alarm for low available space
    try:
        cloudwatch.put_metric_alarm(
            AlarmName=f"LowAvailableSpace-{account_id}",
            AlarmDescription="Alarm when available disk space is less than 10GB",
            MetricName="AvailableDiskSpace",
            Namespace="EC2/DiskUtilization",
            Statistic="Minimum",
            Period=300,
            EvaluationPeriods=2,
            Threshold=10.0,
            ComparisonOperator="LessThanThreshold",
            TreatMissingData="missing",
            Dimensions=[
                {
                    "Name": "InstanceId",
                    "Value": "*"
                }
            ],
            AlarmActions=[
                f"arn:aws:sns:{region}:{account_id}:DiskUtilizationAlerts"
            ]
        )
        print(f"Created low available space alarm for account {account_id}")
    except Exception as e:
        print(f"Error creating low available space alarm: {str(e)}")

def setup_monitoring():
    # Get AWS credentials from environment variables
    aws_accounts = {
        "account_1": {
            "id": os.environ.get("AWS_ACCOUNT_1_ID"),
            "region": os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        },
        "account_2": {
            "id": os.environ.get("AWS_ACCOUNT_2_ID"),
            "region": os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        },
        "account_3": {
            "id": os.environ.get("AWS_ACCOUNT_3_ID"),
            "region": os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        }
    }
    
    # Create SNS topic for alerts
    for account_id, details in aws_accounts.items():
        if details["id"]:
            try:
                sns = boto3.client('sns', region_name=details["region"])
                sns.create_topic(Name="DiskUtilizationAlerts")
                print(f"Created SNS topic for account {details['id']}")
            except Exception as e:
                print(f"Error creating SNS topic: {str(e)}")
            
            # Create dashboard and alarms
            create_cloudwatch_dashboard(details["id"], details["region"])
            create_cloudwatch_alarms(details["id"], details["region"])

if __name__ == "__main__":
    setup_monitoring() 