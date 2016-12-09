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

resp = glacier.initiate_job(
	vaultName=config.get('glacier', 'vault'),
	jobParameters={
		'Type': 'archive-retrieval',
		'ArchiveId':"Y0-Ek1234AAZ4csdf9JcOKj2X0f9lw96PoHzy1t2JxQI_IqccuLDA6Qjc_3mcC4oAmJomfub-ufUBHBLXLdNyt1e0YGXYcIGjWLI5lX7066jHNukzptCTsx79cy5LaqHnueCFOYv5w",
		'SNSTopic': 'arn:aws:sns:us-west-2:892023921805:Test',
	}
)

print resp

'''
