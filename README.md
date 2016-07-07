
aws-help
========

Scripts to help with aws


# Requirements

pip install boto3


# Configuration

- set your regions by changing MY_REGIONS in ec2_reserved_running_report.py
- configure boto aws credentials:
	https://boto3.readthedocs.io/en/latest/guide/quickstart.html#configuration
	http://boto3.readthedocs.io/en/latest/guide/configuration.html#shared-credentials-file


# Usage

- generate report for missing or unused reservations:
	python ec2_reserved_running_report.py | jq


