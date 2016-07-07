MY_REGIONS = ['us-east-1', 'eu-west-1']

import boto3
import json

####
#

def running_instances(MY_REGIONS):
    
    MY_RUNNING = {}
    
    for I_REGION in MY_REGIONS:
    
        ec2 = boto3.resource('ec2', region_name=I_REGION)
        instances = ec2.instances.filter(
                                         Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    
        for instance in instances:
            #print(instance.id, instance.instance_type, instance.placement['AvailabilityZone'])
            '''        
            I_ID = instance.id        
            for tag in instance.tags:
                if tag['Key'] == 'Name':
                    I_ID = tag['Value']
            '''
            
            I_AZ = instance.placement['AvailabilityZone']
            I_TYPE = instance.instance_type
        
            if MY_RUNNING.has_key(I_AZ) == False:
                MY_RUNNING[I_AZ] = {}
        
            if MY_RUNNING[I_AZ].has_key(I_TYPE) == False:
                MY_RUNNING[I_AZ][I_TYPE] = 0
        
            MY_RUNNING[I_AZ][I_TYPE] = MY_RUNNING[I_AZ][I_TYPE] + 1
            
    return MY_RUNNING


def active_reserved(MY_REGIONS):
    
    MY_RESERVED = {}
    
    for I_REGION in MY_REGIONS:
    
        client = boto3.client('ec2', region_name=I_REGION)
        response = client.describe_reserved_instances(
            Filters=[
                {
                    'Name': 'state',
                    'Values': [
                        'active',
                    ]
                }
            ]
        )
        
        for reserve in response['ReservedInstances']:
            #print(reserve['AvailabilityZone'], reserve['InstanceType'], reserve['InstanceCount'])
            
            R_AZ = reserve['AvailabilityZone']
            R_TYPE = reserve['InstanceType']
            R_COUNT = reserve['InstanceCount']            
            
            if MY_RESERVED.has_key(R_AZ) == False:
                MY_RESERVED[R_AZ] = {}
        
            if MY_RESERVED[R_AZ].has_key(R_TYPE) == False:
                MY_RESERVED[R_AZ][R_TYPE] = 0
        
            MY_RESERVED[R_AZ][R_TYPE] = MY_RESERVED[R_AZ][R_TYPE] + R_COUNT
         
    return MY_RESERVED


def compare_reserved_runnin(MY_REGIONS):
    
    MY_RESERVED=active_reserved(MY_REGIONS)
    MY_RUNNING=running_instances(MY_REGIONS)    
    MY_REPORT = {}
    
    for I_AZ in MY_RUNNING:
        for I_TYPE in MY_RUNNING[I_AZ]:                
            #print(I_REGION, I_TYPE, I_DIFF)
            if MY_REPORT.has_key(I_AZ) == False:
                MY_REPORT[I_AZ] = {}
    
            if MY_REPORT[I_AZ].has_key(I_TYPE) == False:
                MY_REPORT[I_AZ][I_TYPE] = 0
                
            if MY_RESERVED[I_AZ].has_key(I_TYPE):
                I_DIFF = MY_RUNNING[I_AZ][I_TYPE] - MY_RESERVED[I_AZ][I_TYPE]
            else:
                I_DIFF = MY_RUNNING[I_AZ][I_TYPE]
                
            MY_REPORT[I_AZ][I_TYPE] = MY_REPORT[I_AZ][I_TYPE] + I_DIFF
            
    for R_AZ in MY_RESERVED:
        for R_TYPE in MY_RESERVED[R_AZ]: 
            if MY_REPORT[R_AZ].has_key(R_TYPE) == False:
                MY_REPORT[R_AZ][R_TYPE] = 0 - MY_RESERVED[R_AZ][R_TYPE]
                
    return MY_REPORT


#print json.dumps(running_instances(MY_REGIONS))            
#print json.dumps(active_reserved(MY_REGIONS))
print json.dumps(compare_reserved_runnin(MY_REGIONS))



