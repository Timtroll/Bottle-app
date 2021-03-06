# coding: utf8
import os

#######################
# Find in DB and upload old files into Amazon Glacier
#
# script A) once process_insertions is complete and the md5 has been processed and the source file moved into the proxies structure, 
# the script will look at the new "archived" field in the asset_media table. if this is set to "n" we will copy file into amazon client, 
# and set the time stamp to the time at which this backup is complete.

# Amazon Workflow:
# 1-st step (archive_new_push.py/archive_old_push.py)
#	- upload files into Glacier. When file has been uploaded we recive hash-code for this file and hash code for retrieve this file. 
#	  Thats all. We dont recive any other data to confirm exists file in the Glacier or not.
# 2-nd step (archive_retrieve.py)
#	- Send request to Gliaicier for retrieve file from Glacier. Message about status we can catch in Amazon SQS.
# 3-d step (archive_pull.py)
#	- Download retrived file.
# 4-d step (archive_pull.py)
#	- Download retrived file.


# Table asset_media columns:
# media_id		- id of media file
# media_name	- real uploaded name of media file (we extract file extention from it)
# media_md5		- md5 name of file for internal storage
# archive		- acrchiving status ('y' - exists in Glacier, 'n' - not exists in Glacier)
# on_disk		- exists file status ('y' - exists on disk, 'n' - not exists on disk)
# archivetime	- date when fil was been upload into Glacier

# Table asset_media_meta columns:
# meta =	archive_id	- id  returned from Glacier
# value =	hashtree		- hash returned from Glacier as confirmation uploading

# This script has limitation 1 row per instance

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
	config.read(fileconf)
else:
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

######### get Amazon connections ############
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

# set current time + 30 days in seconds
curenttime = int(time.time() - 60*60*24*30)

#sql = "SELECT media_id, media_name, media_md5, archive FROM asset_media WHERE on_disk='y' AND archive='n' AND media_md5 IS NOT NULL order by media_id DESC LIMIT 1"

asset_media.execute(sql)

# print all the first cell of all the rows
#for row in asset_media.fetchall():
print("\nStart cicle\n")
while True:
	row = asset_media.fetchone()
	if not row: break

	# create path to file
	print row
	ext = common.fileExt(row[1])
	path = common.getPath(config.get('proxy', 'proxy_dir'), row[2]) + '.' + ext
	print("----------------\n")
	print path

	# check exists file for archiving
	if os.path.exists(path):

		######### create tree hash for confirm upload ############
		hass = common.hass(path)

		######### put file into Glasier #########
		resp = common.PushFile(glacier, sns, config, row[1], path)

		try:
			if resp['checksum'] == hass:
				print "File success uploading. archiveId = " + resp['archiveId']

				asset_media_update = db.cursor()
				curenttime = int(time.time())

				# Insert archive status and archived time into DB
				sql = "UPDATE asset_media SET archive='y', archivetime={0} WHERE media_id={1}".format(curenttime, int(row[0]) )
				asset_media_update.execute(sql)
				db.commit()

				# Insert 'archiveId' into DB
				sql = "INSERT INTO asset_media_meta (media_id, meta, value) VALUES({0}, 'ArchiveId', '{1}') ON DUPLICATE KEY UPDATE meta=VALUES(meta), value=VALUES(value)".format( int(row[0]), str(resp['archiveId']) )
				asset_media_update.execute(sql)
				db.commit()

				# Insert 'tree-hash' into DB
				sql = "INSERT INTO asset_media_meta (media_id, meta, value) VALUES({0}, 'Hashtree', '{1}') ON DUPLICATE KEY UPDATE meta=VALUES(meta), value=VALUES(value)".format( int(row[0]), str(resp['checksum']) )
				asset_media_update.execute(sql)
				db.commit()

		except IndexError:
			print 'File upload with errors:' + resp
	else:

		print 'File not exists:' + path

db.close()
