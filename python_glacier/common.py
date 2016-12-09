# coding: utf8
import boto3
import botocore
import json

from json import dumps

def VaultInfo(name):
	# use Amazon Glacier
	glacier = boto3.client('glacier')

	# get list of exists vaults
	error = ''
	try:
		policy = glacier.get_vault_access_policy(vaultName=name)
	except botocore.exceptions.ClientError as e:
		policy = e.response['Error']['Code']
		error = e.response['Error']['Message']


	if len(error) == 0:
		res = json.dumps(policy)
		info = json.loads(res)

	if len(error) == 0:
		val = json.loads(info['policy']['Policy'])
		return val['Statement'][0]
	else:
		return 0

def VaultsList():
	# use Amazon Glacier
	glacier = boto3.client('glacier')

	# get list of exists vaults
	response = glacier.list_vaults()
	res = json.dumps(response)
	vaults = json.loads(res)

	if len(vaults['VaultList']) > 0:
		return vaults['VaultList']
	else:
		return 0
