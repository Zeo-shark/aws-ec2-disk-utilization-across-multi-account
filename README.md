# AWS Multi-Account Disk Utilization Monitoring

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/downloads/)
[![Ansible](https://img.shields.io/badge/Ansible-2.9+-green.svg)](https://www.ansible.com/)

A comprehensive solution for monitoring disk utilization across multiple AWS accounts using Ansible and AWS CloudWatch. This solution provides real-time monitoring, automated alerts, and centralized dashboards for disk space management across your AWS infrastructure.

## 🌟 Features

- **Multi-Account Support**: Monitor disk utilization across multiple AWS accounts
- **Real-time Monitoring**: CloudWatch dashboards for instant visibility
- **Automated Alerts**: CloudWatch alarms with SNS notifications
- **Custom Metrics**: Detailed disk usage and available space tracking
- **Scalable Architecture**: Easy to add new accounts and instances
- **Security First**: Secure credential management and minimal IAM permissions

## 📋 Prerequisites

- Ansible 2.9 or higher
- Python 3.x
- AWS CLI
- SSH access to EC2 instances
- AWS credentials with appropriate permissions

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/aws-ec2-disk-utilization-across-multi-account.git
cd aws-ec2-disk-utilization-across-multi-account
```

2. Install required Python packages:
```bash
pip install boto3 jinja2
```

3. Set up environment variables for AWS credentials:
```bash
# Account 1
export AWS_ACCOUNT_1_ID="your-account-1-id"
export AWS_ACCOUNT_1_ACCESS_KEY="your-access-key-1"
export AWS_ACCOUNT_1_SECRET_KEY="your-secret-key-1"

# Account 2
export AWS_ACCOUNT_2_ID="your-account-2-id"
export AWS_ACCOUNT_2_ACCESS_KEY="your-access-key-2"
export AWS_ACCOUNT_2_SECRET_KEY="your-secret-key-2"

# Account 3
export AWS_ACCOUNT_3_ID="your-account-3-id"
export AWS_ACCOUNT_3_ACCESS_KEY="your-access-key-3"
export AWS_ACCOUNT_3_SECRET_KEY="your-secret-key-3"
```

## 🚀 Usage

1. Set up CloudWatch monitoring infrastructure:
```bash
python3 ansible/playbooks/aggregate_results.py
```

2. Run the disk utilization playbook:
```bash
ansible-playbook -i ansible/inventory/aws_accounts.yml ansible/playbooks/disk_utilization.yml
```

## 📊 Monitoring

The solution provides:

### CloudWatch Dashboards
- Real-time disk utilization metrics
- Per-instance and aggregated views
- Historical data visualization
- Customizable time ranges

### CloudWatch Alarms
- High disk usage alerts (>80%)
- Low available space alerts (<10GB)
- SNS notifications for critical events
- Configurable thresholds

## 🔐 Security

- **Credential Management**: Secure storage using environment variables
- **IAM Best Practices**: Minimal required permissions
- **SSH Security**: Key-based authentication
- **Access Control**: Role-based access management
- **Audit Trail**: CloudWatch logging

## 📈 Scalability

The solution is designed to scale with:
- Dynamic inventory management
- Parallel execution across accounts
- Efficient metric collection
- Configurable thresholds
- Easy addition of new accounts

## 🛠️ Adding New AWS Accounts

1. Add account details to `ansible/inventory/aws_accounts.yml`:
```yaml
account_4:
  vars:
    aws_account_id: "{{ lookup('env', 'AWS_ACCOUNT_4_ID') }}"
    aws_access_key: "{{ lookup('env', 'AWS_ACCOUNT_4_ACCESS_KEY') }}"
    aws_secret_key: "{{ lookup('env', 'AWS_ACCOUNT_4_SECRET_KEY') }}"
```

2. Set corresponding environment variables
3. Run the monitoring setup script

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
