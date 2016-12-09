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
	'glacier',
	region_name=config.get('glacier', 'region'),
	aws_access_key_id=config.get('credentials', 'aws_access_key_id'),
	aws_secret_access_key=config.get('credentials', 'aws_secret_access_key'),
)

response = glacier.get_vault_notifications(
	vaultName='Tst'
)

print response