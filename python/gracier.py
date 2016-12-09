# coding: utf8
import boto3
import botocore
import MySQLdb

import json
#from collections import namedtuple

#####################
# RabbitMQ

#return array(
#    'host'      => 'localhost',
#    'port'      => 5672,
#    'api_port'  => 15672,
#    'user'      => 'queue_service_api',
#    'password'  => 'test',
#    'vhost'     => '/test'
#);

#####################

'''
#####################
try:
	db = MySQLdb.connect(
		host="localhost",		# your host, usually localhost
		user="test",			# your username
		passwd="test",	# your password
		db="test"				# name of the data base
	)
except db.Error as e:
    print(con.error())

asset_media = db.cursor()
asset_media.execute("SELECT media_id, media_name FROM asset_media")

# print all the first cell of all the rows
#for row in asset_media.fetchall():
while True:
	row = asset_media.fetchone()
	if not row: break
	s = u'='
	res = s.join([str(i) for i in row])
	print(res)

db.close()

exit()

#####################
'''

# use Amazon Glacier
glacier = boto3.client('glacier')

# get list of exists vaults
response = glacier.list_vaults()
res = json.dumps(response)

vaults = json.loads(res)


print vaults['VaultList']
print "============\n"

# get preferense of vaults
for vault in vaults['VaultList']:
	print vault['VaultName']
	print "--"
	
	# get vuult access policy
	try:
		policy = glacier.get_vault_access_policy(vaultName=vault['VaultName'])
	except botocore.exceptions.ClientError as e:
		policy = e.response['Error']['Code'];

	print policy
	print "---\n"
	val = json.loads(policy['policy']['Policy'])
	print val['Statement'][0]['Principal']['AWS']
	print "---\n"

	# put file into 5th_kind vault
	try:
		response = glacier.upload_archive(
			vaultName='5k_vault01',
			archiveDescription='test archive',
			body='../backup/source_backup.tar.gz'
		)
		print response
		print "=-=-=-\n"
		print response['archiveId']
		print "=-=-=-\n"
		# create SNS topic
		topic = sns.create_topic(
			Name=response['archiveId']
		)
	except botocore.exceptions.ClientError as e:
		response = e.response['Error']['Code'];


print response
print "---\n"

# end programm