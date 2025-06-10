# Multi-Account AWS EC2 Disk Utilization Monitoring

### Background:
You are a Solutions architect at a large enterprise that utilizes AWS cloud services. The
company has grown through acquisitions and now manages 3 separate AWS accounts,
each containing numerous EC2 instances. The CTO has expressed concerns about
potential disk space issues across these instances and wants a comprehensive solution
to monitor disk utilization.

### Assignment:
Company is internally using a configuration management tool (Ansible). Before investing
into other tools, the company has decided to use Ansible to perform the required
metric collection.
Design and outline a solution to fetch and report disk utilization from all EC2 instances
across the 3 AWS accounts. Your solution should address the following points:
1. How would you centralize access and management of the 3 AWS accounts?
2. How would you aggregate the collected data from all accounts into a single, easily
digestible format?
3. How would your solution scale if the company acquires more companies and AWS
accounts in the future?

### Deliverables :
- Provide a high-level architectural diagram of your proposed solution.
- Provide the ansible playbook
- Summarize the various component involved in the process