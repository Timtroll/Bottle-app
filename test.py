# coding: utf8
import os

import boto3
import botocore
import json

try:
	import configparser
except:
	from six.moves import configparser

config = configparser.ConfigParser()
config.read("./glacier.ini")

# use Amazon SQS
sqs = boto3.client('sqs')

# get vault name from config
vaultName=config.get('glacier', 'vault')
print(vaultName)

# get list of queues
response = sqs.list_queues(
    QueueNamePrefix=vaultName
)

print(response['QueueUrls'][0])

# get queue url
if (response['QueueUrls'][0]):
	# recive 1 message
	respon = sqs.receive_message(
	    QueueUrl=response['QueueUrls'][0],
	    AttributeNames=[
	        'All',
	    ],
	    MessageAttributeNames=[
	        'test',
	    ],
	    MaxNumberOfMessages=1,
	    VisibilityTimeout=60,
	    WaitTimeSeconds=10,
	)

	if (respon.has_key('Messages')):
		# get 'ReceiptHandle' for deleting message
		if (respon.has_key('ReceiptHandle') and (respon['ResponseMetadata']['HTTPStatusCode'] == 200)):
			print(respon['Messages'][0]['ReceiptHandle'])
			print('Status:')
			print(respon['ResponseMetadata']['HTTPStatusCode'])

			# delete message
			resp = sqs.delete_message(
				QueueUrl='string',
				ReceiptHandle=respon['Messages'][0]['ReceiptHandle']
			)

			# check massage deleting
			prin(resp)
		else:
			print(respon['ResponseMetadata']['HTTPStatusCode']);

	else:
		print('Nothing')
		print(respon)
