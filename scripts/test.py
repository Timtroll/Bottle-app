# coding: utf8
import os
import hashlib
import binascii
import MySQLdb

try:
	import configparser
except:
	from six.moves import configparser

config = configparser.ConfigParser()

fileconf = "/var/www/.otc/core.conf.py"
if os.path.exists(fileconf):
	config.read(fileconf)
else:
	config.read("../includes/core.conf.py")

db = ''
try:
	db = MySQLdb.connect(
		host=config.get('mysqld', 'host'),		# your host, usually localhost
		user=config.get('mysqld', 'user'),		# your username
		passwd=config.get('mysqld', 'passwd'),	# your password
		db=config.get('mysqld', 'db')			# name of the data base
	)
except MySQLdb.DatabaseError, err:
	print(err)


archive_id = '123Hc4awwomOegS0L-4Ama0zO4ZBgeNf9wFEI6X4qc5qXS5LMEJh4L4OX1blgA-wje8oCRBQmdznoT6BxmedjWjoNzZEWlfNZWF9t42qpPO0ypOD8yGBuRLTi6yz4S4erADbbr9KXA'
hashtree = '123bd413427969e54b755e2eaf019525570337256551726b34fd5b2667a527e8'


# check exists retrive request in DB
# prepare db connection
asset_media = db.cursor()

# check exists archiveid in DB
sql = "select media_id from asset_media_meta where meta='ArchiveId' AND value='{0}' AND media_id in (select media_id from asset_media where archive='y' AND on_disk='w' order by media_id)".format( str(archive_id) )
print sql
asset_media.execute(sql)
row1 = asset_media.fetchone()
if row1 is None:
	print "Can not find retrieve request in DB: "
	print row1
print row1

# check exists hashtree in DB
sql = "select media_id from asset_media_meta where meta='Hashtree' AND value='{0}' AND media_id in (select media_id from asset_media where archive='y' AND on_disk='w' order by media_id)".format( str(hashtree) )
print sql
asset_media.execute(sql)
row2 = asset_media.fetchone()
if row2 is None:
	print "Can not find retrieve request in DB: "
	print row2
print row2

if ((row1 is not None) and (row2 is not None) and (row1 == row2)):
	print "меняем"

exit()

'''
filename='/home/timofey/works/code/glacier/scripts/backup/source_backup.tar.Gz'

import os.path 
 
#path, filename = os.path.split(filename) 
basename, extension = os.path.splitext(filename)
print basename
extension = extension.lower()
print extension
exit()

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


print hass(filename)


exit()
'''


'''
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
'''