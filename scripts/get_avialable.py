# coding: utf8
import os

try:
	import configparser
except:
	from six.moves import configparser

import boto3
import botocore
import json

import common

config = configparser.ConfigParser()
config.read("./glacier.ini")


# use Amazon Glacier
glacier = boto3.client(
#glacier = boto3.resource(
	'glacier',
	region_name=config.get('glacier', 'region'),
	aws_access_key_id=config.get('glacier', 'aws_access_key_id'),
	aws_secret_access_key=config.get('glacier', 'aws_secret_access_key'),
)


response = glacier.get_job_output(
    vaultName='Tst',
    jobId='123ZI-KAWdbSg_Vhc8e7c6s2U9J78HNWPlzpdq-2vj0YVRqfH0TB9Z3OdVUXKGcrjl5Ix019gNa-SilUrIiCx27DfC4E',
    range='0-1024'
)

print response
exit()

'''
vault = glacier.describe_vault(vaultName='Tst')
print vault

exit()

vault = glacier.Vault('892023921805', 'Tst')
print vault.jobs.all()

exit()

#notification = glacier.Notification(config.get('glacier', 'account_id'), config.get('glacier', 'vault'))
notification = glacier.Notification('892023921805', 'Tst')
print notification.events
'''


'''
paginator = glacier.get_paginator('list_jobs')

#	accountId=config.get('glacier', 'account_id'),
#	vaultName=config.get('glacier', 'vault'),
#	limit='1000',
#	statuscode='Succeeded',

#	config.get('glacier', 'account_id'),

resp = paginator.paginate(/
	vaultName=config.get('glacier', 'vault'),
	statuscode='Succeeded',
	completed='true',
	PaginationConfig={
		'MaxItems': 123,
		'PageSize': 123,
	}
)
print resp
'''

# for multipart upload?
response = glacier.list_jobs(
	vaultName=config.get('glacier', 'vault'),
	limit='1000',
#	marker='string',
	statuscode='Succeeded',
	completed='true'
)
print response
#print resp.result_keys.JobList


