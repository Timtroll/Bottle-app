# coding: utf8
import os

#######################
# Find in DB and upload old files into Amazon Glacier

# Amazon Workflow:
# 1-st step (archive_push.py)
#	- upload files into Glacier. When file has been uploaded we recive hash-code for this file and hash code for retrieve this file. Thats all. We dont recive any other data to confirm exists file in the Glacier or not.
# 2-nd step (archive_retrieve.py)
#	- Send request to Gliaicier for retrieve file from Glacier. Message about status we can catch in Amazon SQS.
# 3-d step (archive_pull.py)
#	- Download retrived file.

# Database columns:
# media_id		- id of media file
# media_name	- real uploaded name of media file (we extract file extention from it)
# media_md5		- md5 name of file for internal storage
# archive		- acrchiving status ('y' - exists in Glacier, 'n' - not exists in Glacier)
# on_disk		- exists file status:
#					'y' - file exists on disk,
#					'n' - file not exists on disk
#					'r' - need to retrieve file from Glacier
#					'w' - waiting for retrieve file from Glacier
# hashtree		- hash returned from Glacier as confirmation uploading
# archivetime	- date when fil was been upload into Glacier

#######################
# Amazon Glacier config
# AWS_CONFIG_FILE = './amazon.conf'

try:
	import configparser
except:
	from six.moves import configparser

import boto3
import botocore
import MySQLdb
import json
import time

import common

config = configparser.ConfigParser()
# Load config file
fileconf = "/var/www/.otc/core.conf.py"
if os.path.exists(fileconf):
	print fileconf
	config.read(fileconf)
else:
	print "../includes/core.conf.py"
	config.read("../includes/core.conf.py")

db = ''
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

######### get Amazon connection ############
# use Amazon Glacier
glacier = boto3.client(
	'glacier',
	region_name=config.get('glacier', 'region'),
	aws_access_key_id=config.get('glacier', 'aws_access_key_id'),
	aws_secret_access_key=config.get('glacier', 'aws_secret_access_key'),
)

# use Amazon SNS
sns = boto3.client(
	'sns',
	region_name=config.get('glacier', 'region'),
	aws_access_key_id=config.get('glacier', 'aws_access_key_id'),
	aws_secret_access_key=config.get('glacier', 'aws_secret_access_key'),
)


######### get exists Glacier vaults #########
data = common.VaultsList(glacier)

vault_exist = 0
if len(data):
	for dat in data:
		try:
			# check exists vault exit error if need
			val = common.VaultInfo(glacier, dat['VaultName'])
			if dat['VaultName'] == config.get('glacier', 'vault'):
				vault_exist = 1
		except:
			print "Vault {0} from Amazon Glacier not exists in current configuration".format(dat['VaultName'])
#			exit()
else:
	print "Could not connect to Amazon Glacier"
	exit()

# exit if could not find Vault by configuration
if vault_exist != 1:
	print "Could not find Vault {0} by configuration Amazon Glacier".format(config.get('glacier', 'vault'))
	exit()

######### get files for archiving ############
asset_media = db.cursor()
asset_media_meta = db.cursor()
asset_media_update = db.cursor()
#mimes = db.cursor()

sql = "SELECT media_id, media_name, media_md5 FROM asset_media WHERE on_disk='r' AND archive='y' ORDER BY media_id ASC"
asset_media.execute(sql)

# print all the first cell of all the rows
#for row in asset_media.fetchall():
print("\nStart cicle\n")
while True:
	row = asset_media.fetchone()
	if not row: break
	print("----------------\n")
	print row

	# create path to file
	ext = common.fileExt(row[1])
	path = common.getPath(config.get('proxy', 'proxy_dir'), row[2]) + '.' + ext
	print("----------------\n")
	print path

	# Check exists file in proxy structure
#	if os.path.exists(path):
#		print "File already exists on disk"
#		continue
#	else:
	if 1:
		# get ArchiveId for retrive
		sql = "SELECT media_id, meta, value FROM asset_media_meta WHERE meta='ArchiveId' AND media_id={0} ORDER BY media_id DESC LIMIT 1".format( int(row[0]) )
		asset_media_meta.execute(sql)
		metas = asset_media_meta.fetchone()
		if not metas: continue

		# send retrieve request to restore file from Glasier
		jobid = common.ReceiveArhive(glacier, config, metas[2])

		# store jobId if retrieve starting and change on_disk status to 'w'
		try:
			if 'jobId' in jobid:
				# check exists meta information jobId for Glacier
				sql = "SELECT count(*) FROM asset_media_meta WHERE media_id={0} AND meta='jobId'".format( int(metas[0]) )
				print sql
				asset_media_update.execute(sql)
				count = asset_media_update.fetchone()

				if (count[0] == 0):
					# Insert 'jobId' into DB
					sql = "INSERT INTO asset_media_meta SET media_id={0}, meta='jobId', value='{1}'".format( int(metas[0]), str(jobid['jobId']) )
					print sql
					asset_media_update.execute(sql)
					db.commit()
				else:
					# Update 'jobId' in DB
					sql = "UPDATE asset_media_meta SET value='{0}' WHERE media_id={1} AND meta='jobId'".format( str(jobid['jobId']), int(metas[0]) )
					print sql
					asset_media_update.execute(sql)
					db.commit()

				# change on_disk status 'r' to 'w'
				sql = "UPDATE asset_media SET on_disk='w' WHERE media_id={0} AND on_disk='r'".format( int(row[0]) )
				print sql
				asset_media_update.execute(sql)
				db.commit()

				print 'Glacier starting retrieve job. Please wait 3-5 hour to complete. jobId:' + jobid['jobId']
			else:
				print 'Glacier do not send jobId:' + str(jobid)
		except IndexError:
			print 'Could not success retrieve file from Glacier:' + jobid
db.close()
