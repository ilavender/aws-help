
aws-help
========

very simple reserved instances monitor.
return json list:

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

```
  -i          list running instances (instance type and availability zone)
  -r          list active reserved (instance type and availability zone)
  -a          list action of reserved to buy or sell (instance type and
              availability zone)
```


