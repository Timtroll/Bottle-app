# coding: utf8
import os.path 
import boto3
import botocore
import hashlib
import binascii
import json

from json import dumps

# send retrieve request to restore file from Glasier
def ReceiveArhive(glacier, config, name):
	# Get name of SNSTopic (like arn:aws:sns:us-west-2:DDDDDDDDDD:WWWWWW)
	val = ['arn', 'aws', 'sns', str(config.get('glacier', 'region')), str(config.get('glacier', 'account_id')), str(config.get('glacier', 'sns_topic'))]
	snstopic = ':'.join(val)

	# Send retrieve request
	try:
		resp = glacier.initiate_job(
			vaultName = config.get('glacier', 'vault'),
			jobParameters = {
				'Type'		: 'archive-retrieval',
				'ArchiveId'	: name,
				'SNSTopic'	: str(snstopic)
			}
		)

		if (resp['ResponseMetadata']['HTTPStatusCode'] != 202):
			print "Unsuccess request for retrieve" + resp

	except botocore.exceptions.ClientError as e:
		resp = e
#		resp = e.resp['Error']['Code'];
#	except Exception:
#		resp = 'Request error InitiateJob'
#		print 'Request error InitiateJob'

	return resp

# get vault info from Glasier
def VaultInfo(glacier, name):
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

# get vaults list from Glasier
def VaultsList(glacier):
	# get list of exists vaults
	response = glacier.list_vaults()
	res = json.dumps(response)
	vaults = json.loads(res)

	if len(vaults['VaultList']) > 0:
		return vaults['VaultList']
	else:
		return 0

# put file into Glasier
def PushFile(glacier, sns, config, file, path):
	print("PushFile")
	print(file)
	print(path)
	print("To " + config.get('glacier', 'vault'))

	f = open(path, 'rb')

	# put file into Glacier vault
	try:
		response = glacier.upload_archive(
			vaultName=config.get('glacier', 'vault'),
			archiveDescription=file,
			body=f.read()
		)
		if (response['ResponseMetadata']['HTTPStatusCode'] != 201):
			print("Unsuccess push\n")

	except botocore.exceptions.ClientError as e:
		print e
		response = e.response['Error']['Code'];

	f.close()

	return response

def CreateSnsTopic(sns, topic):
	# create SNS topic
	topic = sns.create_topic(
		Name=topic
	)

def treehash(input):
	output = []
	while len(input) > 1:
		h1 = input.pop(0)
		h2 = input.pop(0)
		output.append(hashlib.sha256(h1 + h2).digest())
	if len(input) == 1:
		output.append(input.pop(0))
	if len(output) > 1:
		output = treehash(output[:])
	return output

def hass(filename):
	hashes = []
	try:
		file = open(filename,'r')
	except:
		print "Failed to open file: %s" % ( filename )
		sys.exit(1)
	buf = file.read(1024 * 1024)
	while len(buf) != 0:
		hashes.append(hashlib.sha256(buf).digest())
		buf = file.read(1024 * 1024)
	file.close()
	hash = treehash(hashes[:])
	return "%s" % ( binascii.hexlify(hash[0]) )

######### Path & file utilites ######### 
def getPath (root_path, md5):
	path = md5[0:3]
	folder = str(root_path) + '/' + str(path) + '/'
	path = folder + str(md5)

	# check dir and create if not exists
	folder = os.path.dirname(folder)

	if not os.path.exists(folder):
		os.makedirs(folder)

	return path

def fileExt (filename):
	basename, extension = os.path.splitext(filename)
	extension = extension.lower()
	extension = extension.replace('.', '')

	return extension

