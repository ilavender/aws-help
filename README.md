
aws-help
========

very simple reserved instances monitor.
return json list:

- ReservedAction (what need to buy/sell) 
- Budget (buy actions only)


# Requirements

pip install boto3


# Configuration

- set your regions by changing MY_REGIONS in ec2_reserved_running_report.py
- configure boto aws credentials:
```
	https://boto3.readthedocs.io/en/latest/guide/quickstart.html#configuration
	http://boto3.readthedocs.io/en/latest/guide/configuration.html#shared-credentials-file
```


# Usage

- generate report for missing or unused reserved instances:
```
	python ec2_reserved_running_report.py | jq .
```


