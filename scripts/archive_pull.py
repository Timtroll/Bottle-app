# coding: utf8
import os

import boto3
import botocore
import MySQLdb
import json
from collections import namedtuple

try:
	import configparser
except:
	from six.moves import configparser

config = configparser.ConfigParser()

# Load config file
fileconf = "/var/www/.otc/core.conf.py"
if os.path.exists(fileconf):
	config.read(fileconf)
else:
	config.read("../includes/core.conf.py")

######### get DB connection ############
try:
	db = MySQLdb.connect(
		host=config.get('mysqld', 'host'),		# your host, usually localhost
		user=config.get('mysqld', 'user'),		# your username
		passwd=config.get('mysqld', 'passwd'),	# your password
		db=config.get('mysqld', 'db')			# name of the data base
	)
except MySQLdb.DatabaseError, err:
	print(err)

# use Amazon Glacier
glacier = boto3.client(
	'glacier',
	region_name=config.get('glacier', 'region'),
	aws_access_key_id=config.get('glacier', 'aws_access_key_id'),
	aws_secret_access_key=config.get('glacier', 'aws_secret_access_key'),
)

# use resource Amazon Glacier
resour = boto3.resource(
	'glacier',
	region_name=config.get('glacier', 'region'),
	aws_access_key_id=config.get('glacier', 'aws_access_key_id'),
	aws_secret_access_key=config.get('glacier', 'aws_secret_access_key'),
)

# use Amazon SQS
sqs = boto3.client(
	'sqs',
	region_name=config.get('glacier', 'region'),
	aws_access_key_id=config.get('glacier', 'aws_access_key_id'),
	aws_secret_access_key=config.get('glacier', 'aws_secret_access_key'),
)


# get vault name from config
vaultName=config.get('glacier', 'sqs_topic')
print(vaultName)

# get list of queues
response = sqs.list_queues(
	QueueNamePrefix=vaultName
)

#print(response)
#print(response['QueueUrls'][0])
#response['QueueUrls'][0]

# get message from queue url
#sqs.list_queues(
#	QueueNamePrefix=vaultName
#)

# get queue url
if (response['ResponseMetadata']['HTTPStatusCode'] == 200):
	# recive 1 message
	respon = sqs.receive_message(
		QueueUrl=response['QueueUrls'][0],
		AttributeNames=[
			'All',
		],
		MessageAttributeNames=[
			'all',
		],
		MaxNumberOfMessages=1,
		VisibilityTimeout=60,
		WaitTimeSeconds=20,
	)

	print len(respon['Messages'])
	print respon['Messages']

	# convert json response into obj
	mesg = json.loads(respon['Messages'][0]['Body'])
	messg = json.loads(mesg['Message'])

	action = messg['Action']

	if (action == 'ArchiveRetrieval'):
		archive_id = messg['ArchiveId']
		hashtree = messg['ArchiveSHA256TreeHash']
		jobId = messg['JobId']

		file_range = messg['RetrievalByteRange']
		status_code = messg['StatusCode']

		# check exists retrive request in DB
		# prepare db connection
		asset_media = db.cursor()
		asset_media_update = db.cursor()

		# check exists archiveid in DB
		sql = "select media_id from asset_media_meta where meta='ArchiveId' AND value='{0}' AND media_id in (select media_id from asset_media where archive='y' AND on_disk='w' order by media_id)".format( str(archive_id) )
		asset_media.execute(sql)
		row1 = asset_media.fetchone()
		if row1 is None:
			print "Can not find retrieve request in DB: "
			print row1

		# check exists hashtree in DB
		sql = "select media_id from asset_media_meta where meta='Hashtree' AND value='{0}' AND media_id in (select media_id from asset_media where archive='y' AND on_disk='w' order by media_id)".format( str(hashtree) )
		asset_media.execute(sql)
		row2 = asset_media.fetchone()
		if row2 is None:
			print "Can not find retrieve request in DB: "
			print row2

		# download file from Glacier if exists in DB
		if ((row1 is not None) and (row2 is not None) and (row1 == row2)):
			# get file name and md5 from DB
			sql = "select media_id, media_name from asset_media where media_id={0} LIMIT 1".format( int(row1) )
			asset_media.execute(sql)
			media_md5[0] = asset_media.fetchone()
			if not media_md5:
				print "Can not media_id in DB"
				exit()

			# get path to proxy dir
			ext = common.fileExt(media_md5[1])
			out_file = common.getPath(config.get('proxy', 'proxy_dir'), media_md5[0]) + '.' + ext

			# prepare downloading from from Amazon Glacier
			job = resour.Job(
				config.get('glacier', 'account_id'),
				config.get('glacier', 'vault'),
				jobId
			)

			# get file handle from Amazon Glacier
			response = glacier.get_job_output(
				vaultName=config.get('glacier', 'vault'),
				jobId=jobId,
				range=file_range
			)

			# download file stored in Glacier
			response = job.get_output( range=file_range )

			# store retrived file
			f1 = open(out_file, "wb")
			f1.write(response['body'].read())
			f1.close

			# if download file is success
			if os.path.exists(out_file):
				print "Success download file: " + out_file

				# change status file in DB
				sql = "UPDATE asset_media_meta SET value='{0}' WHERE media_id={1} AND meta='ArchiveId'".format( str(resp['archiveId']), int(row[0]) )
				print sql
				asset_media_update.execute(sql)
				db.commit()

				sql = "UPDATE asset_media_meta SET value='{0}' WHERE media_id={1} AND meta='ArchiveId'".format( str(resp['archiveId']), int(row[0]) )
				print sql
				asset_media_update.execute(sql)
				db.commit()

				# delete jobId from asset_media_meta table

				# delete message
				resp = sqs.delete_message(
					QueueUrl=response['QueueUrls'][0],
					ReceiptHandle=respon['Messages'][0]['ReceiptHandle']
				)

				# check message deleting
				if (resp['ResponseMetadata']['HTTPStatusCode'] == 200):
					print('Deleting OK')
					print(resp)
				else:
					print('Deleting error')
					print(resp)
			else:
				print "File: " + out_file

	else:
		print "Not correct message form SQS: "
		print respon
		exit()


	exit()

	if (respon.has_key('Messages')):
		# get 'ReceiptHandle' for deleting message
		if ((len(respon['Messages']) > 0) and (respon['ResponseMetadata']['HTTPStatusCode'] == 200)):
			print(respon['Messages'][0]['ReceiptHandle'])
			print('Status:')
			print(respon['ResponseMetadata']['HTTPStatusCode'])

			# delete message
			resp = sqs.delete_message(
				QueueUrl=response['QueueUrls'][0],
				ReceiptHandle=respon['Messages'][0]['ReceiptHandle']
			)

			# check message deleting
			if (resp['ResponseMetadata']['HTTPStatusCode'] == 200):
				print('Deleting OK')
				print(resp)
			else:
				print('Deleting error')
				print(resp)
		else:
			print(respon['ResponseMetadata']['HTTPStatusCode']);

	else:
		print('Nothing')
		print(respon)
else:
	print('Nothing messages')