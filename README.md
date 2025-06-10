# aws-ec2-disk-utilization-across-multi-account




## Overview

This repository provides a resilient, secure, and scalable solution to monitor disk utilization across multiple AWS accounts using Ansible. It leverages AWS Organizations for centralized account management, cross-account IAM roles for secure access, and stores aggregated metrics in S3 for visualization.

![./docs\diagrams\cross-account-ec2-monitoring.drawio.png](./docs\diagrams\cross-account-ec2-monitoring.drawio.png)

## Features

- ✅ **Multi-Account Support** - Monitor across multiple AWS accounts
- ✅ **Scalable Architecture** - Can scale to thousands of ec2 instances
- ✅ **Automated Reporting** - Real-time dashboards and alerts
- ✅ **Security First** - Cross-account roles with least privilege
- ✅ **Cost Optimized** - Efficient data storage and processing
- ✅ **Easy Onboarding** - Automated new account integration

## Quick Start

### Prerequisites
- AWS CLI configured with appropriate permissions
- Ansible 2.12+ installed
- Python 3.8+ with boto3
- Terraform 1.0+ (optional)

## Repository Structure

```plaintext
multi-account-ec2-disk-monitoring/
├── ansible/
│   ├── inventories/            # Grouped AWS accounts inventories
│   │   ├── prod_accounts.yml
│   │   └── staging_accounts.yml
│   ├── playbooks/              # Main playbooks
│   │   └── gather_disk_metrics.yml
│   ├── roles/                  # Reusable Ansible roles
│   │   ├── common/
│   │   ├── aws_credentials/
│   │   └── ec2_disk_monitor/
│   └── ansible.cfg             # Ansible configuration
├── docs/
│   ├── diagrams/               # Architecture and flow diagrams
│   │   └── architecture.png
│   └── implementation_steps.md # Detailed setup instructions
├── .github/
│   └── workflows/              # CI/CD pipelines
│       └── ansible-lint.yml
├── README.md                   # This file
└── LICENSE                     # License information
```
