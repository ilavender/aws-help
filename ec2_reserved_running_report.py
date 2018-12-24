#!/usr/bin/env python

MY_REGIONS = ['us-east-1', 'eu-west-1']

import boto3
import json, argparse, re, csv

parser = argparse.ArgumentParser()
parser.add_argument('-i', action='store_true', dest='list_running',
                    help='list running instances (instance type and availability zone)')
parser.add_argument('-r', action='store_true', dest='list_reserved',
                    help='list active reserved (instance type and availability zone)')
parser.add_argument('-a', action='store_true', dest='list_action',
                    help='list action of reserved to buy or sell (instance type and availability zone)')
parser.add_argument('-csv', action='store', dest='csv_file',
                    help='file name/path for CSV dump')
args = parser.parse_args()


####
#

def running_instances(MY_REGIONS):
    
    
    if args.list_running:                
        MY_RUNNING = []                
    else:
        MY_RUNNING = {}
    
    for I_REGION in MY_REGIONS:
    
        ec2 = boto3.resource('ec2', region_name=I_REGION)
        instances = ec2.instances.filter(
                                         Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    
        for instance in instances:
            #print(instance.id, instance.instance_type, instance.placement['AvailabilityZone'])
            #print(json.dumps(instance.tags))
            
            I_ID = instance.id
            I_NAME = None
            
            for tag in instance.tags:
                if tag['Key'] == 'Name':
                    I_NAME = tag['Value']
            
            if instance.vpc_id:
                I_PLATFORM = 'Linux/UNIX (Amazon VPC)'
            else:
                I_PLATFORM = 'Linux/UNIX'
                
            if args.list_running:           
                MY_RUNNING.append({
                    'InstancesName':I_NAME,
                    'InstancesId':I_ID,
                    'Region': I_REGION,
                    'InstanceType':instance.instance_type, 
                    'AvailabilityZone':instance.placement['AvailabilityZone'], 
                    'ProductDescription':I_PLATFORM
                    })
            else:            
                                
                I_TYPE = instance.instance_type                
            
                if MY_RUNNING.has_key(I_REGION) == False:
                    MY_RUNNING[I_REGION] = {}
                    
                if MY_RUNNING[I_REGION].has_key(I_PLATFORM) == False:
                    MY_RUNNING[I_REGION][I_PLATFORM] = {}
            
                if MY_RUNNING[I_REGION][I_PLATFORM].has_key(I_TYPE) == False:
                    MY_RUNNING[I_REGION][I_PLATFORM][I_TYPE] = 0
            
                MY_RUNNING[I_REGION][I_PLATFORM][I_TYPE] = MY_RUNNING[I_REGION][I_PLATFORM][I_TYPE] + 1
            
    return MY_RUNNING


def active_reserved(MY_REGIONS): 
    
    if args.list_reserved:                
        MY_RESERVED = []                
    else:
        MY_RESERVED = {}     
    
    for I_REGION in MY_REGIONS:
    
        client = boto3.client('ec2', region_name=I_REGION)
        response = client.describe_reserved_instances(
            Filters=[
                {
                    'Name': 'state',
                    'Values': [
                        'active',
                        'payment-pending'
                    ]
                }
            ]
        )
        
        for reserve in response['ReservedInstances']:
            #print(reserve['ReservedInstancesId'], reserve['AvailabilityZone'], reserve['InstanceType'], reserve['InstanceCount'])            
            R_PLATFORM = reserve['ProductDescription']
            
            if args.list_reserved:
                offering = find_offering(I_REGION, reserve['InstanceType'], R_PLATFORM)
                MY_RESERVED.append({
                    'ReservedInstancesId': reserve['ReservedInstancesId'], 
                    'Region': I_REGION,
                    'InstanceType': reserve['InstanceType'],
                    'InstanceCount': reserve['InstanceCount'],
                    'ProductDescription': reserve['ProductDescription'],
                    'upfront':(offering['FixedPrice'] * reserve['InstanceCount'])
                    })
            else:                
                #R_AZ = reserve['AvailabilityZone']
                R_TYPE = reserve['InstanceType']
                R_COUNT = reserve['InstanceCount']                
                    
                if MY_RESERVED.has_key(I_REGION) == False:
                    MY_RESERVED[I_REGION] = {}
            
                if MY_RESERVED[I_REGION].has_key(R_PLATFORM) == False:
                    MY_RESERVED[I_REGION][R_PLATFORM] = {}
                    
                if MY_RESERVED[I_REGION][R_PLATFORM].has_key(R_TYPE) == False:
                    MY_RESERVED[I_REGION][R_PLATFORM][R_TYPE] = 0
            
                MY_RESERVED[I_REGION][R_PLATFORM][R_TYPE] = MY_RESERVED[I_REGION][R_PLATFORM][R_TYPE] + R_COUNT
            
    return MY_RESERVED


def compare_reserved_runnin(MY_REGIONS):
    
    MY_RESERVED=active_reserved(MY_REGIONS)
    MY_RUNNING=running_instances(MY_REGIONS)    
    MY_REPORT = {}
    
    for REGION in MY_RUNNING:
        for I_PLATFORM in MY_RUNNING[REGION]:
            for I_TYPE in MY_RUNNING[REGION][I_PLATFORM]:                
                #print(I_REGION, I_TYPE, I_DIFF)
                if MY_REPORT.has_key(REGION) == False:
                    MY_REPORT[REGION] = {}
                
                if MY_REPORT[REGION].has_key(I_PLATFORM) == False:
                    MY_REPORT[REGION][I_PLATFORM] = {}
                
                if MY_REPORT[REGION][I_PLATFORM].has_key(I_TYPE) == False:
                    MY_REPORT[REGION][I_PLATFORM][I_TYPE] = 0
                    
                if MY_RESERVED.has_key(REGION) and MY_RESERVED[REGION].has_key(I_PLATFORM) and MY_RESERVED[REGION][I_PLATFORM].has_key(I_TYPE):
                    I_DIFF = MY_RUNNING[REGION][I_PLATFORM][I_TYPE] - MY_RESERVED[REGION][I_PLATFORM][I_TYPE]
                else:
                    I_DIFF = MY_RUNNING[REGION][I_PLATFORM][I_TYPE]
                    
                MY_REPORT[REGION][I_PLATFORM][I_TYPE] = MY_REPORT[REGION][I_PLATFORM][I_TYPE] + I_DIFF
            
    for REGION in MY_RESERVED:
        for R_PLATFORM in MY_RESERVED[REGION]:
            for R_TYPE in MY_RESERVED[REGION][R_PLATFORM]:
                if MY_REPORT[REGION].has_key(R_PLATFORM) == False:
                    MY_REPORT[REGION][R_PLATFORM] = {}
                     
                if MY_REPORT[REGION][R_PLATFORM].has_key(R_TYPE) == False:
                    MY_REPORT[REGION][R_PLATFORM][R_TYPE] = 0 - MY_RESERVED[REGION][R_PLATFORM][R_TYPE]
                
    return MY_REPORT


def find_offering(REGION, TYPE,I_PLATFORM):
    
    #REGION = AZ[:-1]
    client = boto3.client('ec2', region_name=REGION)

    response = client.describe_reserved_instances_offerings(
        InstanceType=TYPE,
        ProductDescription=I_PLATFORM,    
        InstanceTenancy='default',
        OfferingType='All Upfront',
        OfferingClass='convertible',
        IncludeMarketplace=False,
        MinDuration=31536000,
        MaxDuration=31536000,
        MaxResults=1
    )
    
    for offering in response['ReservedInstancesOfferings']:
        #print json.dumps(offering)                
        return {'FixedPrice':offering['FixedPrice'], 'RecurringCharges':offering['RecurringCharges'], 'CurrencyCode':offering['CurrencyCode']}



def action_report(MY_REGIONS):

    MY_REPORT = compare_reserved_runnin(MY_REGIONS)
    WISH_LIST = []
    WISH_LIST_BUDGET = 0
    
    for REGION in MY_REPORT:
        for I_PLATFORM in MY_REPORT[REGION]:
            for I_TYPE in MY_REPORT[REGION][I_PLATFORM]:
                if MY_REPORT[REGION][I_PLATFORM][I_TYPE] > 0:
                    offering = find_offering(REGION, I_TYPE, I_PLATFORM)
                    upfront = (MY_REPORT[REGION][I_PLATFORM][I_TYPE] * offering['FixedPrice'])
                    FixedPrice = offering['FixedPrice']
                    WISH_LIST_BUDGET = WISH_LIST_BUDGET + upfront
                    ACTION = 'Buy' 
                elif MY_REPORT[REGION][I_PLATFORM][I_TYPE] < 0:
                    FixedPrice = 0
                    ACTION = 'Sell'
                elif MY_REPORT[REGION][I_PLATFORM][I_TYPE] == 0:
                    FixedPrice = 0
                    ACTION = 'NA'
                    continue
                
                WISH_LIST.append({'Region':REGION, 'ProductDescription': I_PLATFORM, 'InstanceType':I_TYPE, 'InstanceCount':MY_REPORT[REGION][I_PLATFORM][I_TYPE], 'FixedPrice':FixedPrice, 'Action':ACTION})
            
    return WISH_LIST


def csv_report(data, csvfile):
    with open(csvfile, "w") as file_handler:
        csv_file = csv.writer(file_handler)
        csv_file.writerow(data[0].keys())
        for item in data:
            csv_file.writerow(item.values())
    return


if args.list_running:
    if args.csv_file != None:
        csv_report(running_instances(MY_REGIONS), args.csv_file)
    print(json.dumps(running_instances(MY_REGIONS)))
elif args.list_reserved:
    if args.csv_file != None:
        csv_report(active_reserved(MY_REGIONS), args.csv_file)
    print(json.dumps(active_reserved(MY_REGIONS)))         
elif args.list_action and args.list_reserved == False and args.list_running == False:
    if args.csv_file != None:
        csv_report(action_report(MY_REGIONS), args.csv_file)
    print(json.dumps(action_report(MY_REGIONS)))
    #print json.dumps({'ReservedAction':WISH_LIST, 'Budget':WISH_LIST_BUDGET})

#print json.dumps(active_reserved(MY_REGIONS))
#print json.dumps(compare_reserved_runnin(MY_REGIONS))
#print json.dumps(find_offering('eu-west-1a', 'm4.xlarge'))

