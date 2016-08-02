
aws-help
========

very simple reserved instances monitor.
return json list

# Note

competible only with Linux classic or vpc.
<br>
product family: 'Linux/UNIX (Amazon VPC)' and 'Linux/UNIX'.
<br>
Reserved pricing refer to 'Partial Upfront' for 1 year.

# Requirements

pip install boto3


# Configuration

- configure boto aws credentials:

	https://boto3.readthedocs.io/en/latest/guide/quickstart.html#configuration
<br>
	http://boto3.readthedocs.io/en/latest/guide/configuration.html#shared-credentials-file

- set your regions by changing MY_REGIONS in ec2_reserved_running_report.py


# Usage

```
  -i          list running instances

	  {
	    "InstancesId": "i-XXXXXX",
	    "AvailabilityZone": "eu-west-1a",
	    "InstancesName": "machine.domain.com",
	    "InstanceType": "m3.large",
	    "ProductDescription": "Linux/UNIX (Amazon VPC)"
	  }

  -r          list active reserved

	  {
	    "ReservedInstancesId": "XXXXX-XXXXX-XXXXX",
	    "AvailabilityZone": "eu-west-1a",
	    "InstanceType": "m3.large",
	    "ProductDescription": "Linux/UNIX (Amazon VPC)",
	    "InstanceCount": 3
	  }

  -a          list action of reserved to buy or sell 

	  {
	    "FixedPrice": 62,
	    "ProductDescription": "Linux/UNIX",
	    "AvailabilityZone": "eu-west-1a",
	    "Action": "Buy",
	    "InstanceType": "t1.micro",
	    "InstanceCount": 1
	  }
```


