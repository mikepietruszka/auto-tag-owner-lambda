#!/usr/bin/env python
'''
Tag an instance with the owner name of who created it.


.. moduleauthor:: Mike Pietruszka <mike@mpietruszka.com>
'''

import boto3
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_instances():
    instances = []
    for reservation in ec2_client.describe_instances()['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance['InstanceId'])
    return instances


def get_instance_status(instance_id):
    instance = ec2_resoruce.Instance(instance_id)
    return instance.state['Name']


def get_tags(instance_id):
    instance = ec2_resource.Instance(instance_id)
    #for tags in instance.tags:
    #    print(tags['Key'])
    return instance


def get_run_instances_username(instance_id):
    '''
    Events can only be looked up by one attribute. That sucks :(
    Also things get throttled here at one call per second.

    Other interesting attributes:
    {
        'AttributeKey': 'EventName',
        'AttributeValue': 'RunInstances'
    },
    {
        'AttributeKey': 'ResourceType',
        'AttributeValue': 'EC2 Instance' 
    },
    {
        'AttributeKey': 'ResourceName',
        'AttributeValue': 'i-08ddfe1e51bb6c965'
    }
    '''
    events = ct_client.lookup_events(
        LookupAttributes=[
            {
                'AttributeKey': 'ResourceName',
                'AttributeValue': instance_id
            }
        ],
        StartTime=datetime(2017, 12, 01)
    )

    for event in events['Events']:
        if event['EventName'] == 'RunInstances':
            username = event['Username']
    return username


def tag_instance(username, instance_id):
    try:
        if get_instance_status(instance_id) == 'running':
            instance.create_tags(
                DryRun=False,
                Tags=[
                    {
                        'Key': 'owner',
                        'Value': username
                    }
                ]
            )
    except:
        logging.error("Failed to tag instance {0}".format(instance_id))
    else:
        if result['ResponseMetadata']['HTTPStatusCode'] == 200:
            logger.info("Successfully created tags for instance {0}"
                .format(instance_id))


def lambda_handler(event, context):
    try:
        session = boto3.session.Session(region_name=event['region_name'])
    except:
        raise Exception("ERROR: error")
    else:    
        ec2_client = session.client('ec2')
        ec2_resource = session.resource('ec2')
        ct_client = session.client('cloudtrail')

    instances = get_instances()

    for instance_id in instances:
        username = get_run_instances_username(instance_id)
        tag_instance(username, instance_id)

    logging.info("Tagged the following instances: {0}.format(instances)")