# Manual IAM Setup Guide for Cross-Account Disk Metrics Collection

This guide provides step-by-step instructions for setting up cross-account access for disk metrics collection using the AWS Management Console.

## Prerequisites

1. Access to AWS Management Console for both management and member accounts
2. AWS Organizations setup with management account and member accounts
3. Note down the following information:
   - Management Account ID
   - Member Account IDs
   - Generate a secure External ID (you can use a UUID generator)

## Step 1: Create IAM Policy in Member Accounts

In each member account, create a policy for disk metrics collection:

1. Go to IAM → Policies → Create Policy
2. Choose JSON tab and paste the following policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeTags",
                "ec2:DescribeVolumes"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "cloudwatch:PutMetricData",
                "cloudwatch:GetMetricData",
                "cloudwatch:ListMetrics"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "cloudwatch:namespace": "EC2/DiskUtilization"
                }
            }
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:log-group:/aws/disk-metrics/*"
        }
    ]
}
```

3. Click "Next: Tags" (add tags if needed)
4. Click "Next: Review"
5. Name the policy: `DiskMetricsCollectionPolicy`
6. Add description: "Policy for collecting EC2 disk metrics and sending to CloudWatch"
7. Click "Create Policy"

## Step 2: Create IAM Role in Member Accounts

In each member account, create a role that the management account can assume:

1. Go to IAM → Roles → Create Role
2. Select "AWS Account" as the trusted entity
3. Select "Another AWS Account" and enter the Management Account ID
4. Check "Require External ID" and enter the External ID you generated
5. Click "Next: Permissions"
6. Search for and select the `DiskMetricsCollectionPolicy` created in Step 1
7. Click "Next: Tags" (add tags if needed)
8. Click "Next: Review"
9. Name the role: `DiskMetricsCollectorRole`
10. Add description: "Role for cross-account disk metrics collection"
11. Click "Create Role"

## Step 3: Create IAM Policy in Management Account

In the management account, create a policy for assuming the member account roles:

1. Go to IAM → Policies → Create Policy
2. Choose JSON tab and paste the following policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": [
                "arn:aws:iam::*:role/DiskMetricsCollectorRole"
            ],
            "Condition": {
                "StringEquals": {
                    "sts:ExternalId": "YOUR_EXTERNAL_ID"
                }
            }
        }
    ]
}
```

3. Replace `YOUR_EXTERNAL_ID` with the External ID you generated
4. Click "Next: Tags" (add tags if needed)
5. Click "Next: Review"
6. Name the policy: `AssumeDiskMetricsRolePolicy`
7. Add description: "Policy for assuming disk metrics collector roles in member accounts"
8. Click "Create Policy"

## Step 4: Create IAM Role in Management Account

In the management account, create a role for the Ansible control host:

1. Go to IAM → Roles → Create Role
2. Select "AWS Service" as the trusted entity
3. Select "EC2" as the service
4. Click "Next: Permissions"
5. Search for and select the `AssumeDiskMetricsRolePolicy` created in Step 3
6. Click "Next: Tags" (add tags if needed)
7. Click "Next: Review"
8. Name the role: `AnsibleDiskMetricsRole`
9. Add description: "Role for Ansible control host to collect disk metrics"
10. Click "Create Role"

## Step 5: Update Ansible Configuration

Update your Ansible inventory file with the role ARNs:

```yaml
all:
  children:
    aws_accounts:
      children:
        account_1:
          vars:
            aws_account_id: "MEMBER_ACCOUNT_1_ID"
            role_arn: "arn:aws:iam::MEMBER_ACCOUNT_1_ID:role/DiskMetricsCollectorRole"
            external_id: "YOUR_EXTERNAL_ID"
        account_2:
          vars:
            aws_account_id: "MEMBER_ACCOUNT_2_ID"
            role_arn: "arn:aws:iam::MEMBER_ACCOUNT_2_ID:role/DiskMetricsCollectorRole"
            external_id: "YOUR_EXTERNAL_ID"
        account_3:
          vars:
            aws_account_id: "MEMBER_ACCOUNT_3_ID"
            role_arn: "arn:aws:iam::MEMBER_ACCOUNT_3_ID:role/DiskMetricsCollectorRole"
            external_id: "YOUR_EXTERNAL_ID"
```

## Security Best Practices

1. **External ID**:
   - Keep the External ID secure
   - Rotate it periodically
   - Use different External IDs for different environments

2. **IAM Policies**:
   - Follow the principle of least privilege
   - Regularly review and audit policies
   - Remove unused policies and roles

3. **Role Assumption**:
   - Use External ID for additional security
   - Limit the scope of assumable roles
   - Monitor role usage through CloudTrail

4. **Monitoring**:
   - Enable CloudTrail logging
   - Set up CloudWatch alarms for IAM changes
   - Regularly review access patterns
