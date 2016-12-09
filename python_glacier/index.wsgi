# coding: utf8
import os
os.chdir(os.path.dirname(__file__))

from bottle import debug, default_app, run, get, route, template, view
from bottle import response
#from bottle import *

import common

import arch
import check

####### API #######

@route("/arch_new/")
def arch_new():
	response.content_type = 'application/json'
	data = arch.ArchNew()
	return data

@route("/arch_old/")
def arch_old():
	response.content_type = 'application/json'
	data = arch.ArchOld()
	return data

@route("/check_uploaded/")
def check_uploaded():
	response.content_type = 'application/json'
	data = check.CheckUploaded()
	return data

@route("/check_recovery/")
def check_recovery():
	response.content_type = 'application/json'
	data = check.CheckRecovery()
	return data


####### Web interface #######

@route("/info/<name>/")
def info(name=None):
	data = common.VaultInfo(name)
	return template('info', data=data)

@route("/list")
def list():
	data = common.VaultsList()
	return template('list', data=data)

#@get('/')
#@view("base")
@route("/")
def vlist():
#	response.content_type = 'application/json'
	data = common.VaultsList()
	return template('list', data=data)

# Start the short timer.  
#short_time()

# Start the long timer.  
long_time()


debug(True)
#run(app, host='0.0.0.0', port=4444, reloader=True)
application = default_app()