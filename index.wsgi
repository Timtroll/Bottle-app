import os
os.chdir(os.path.dirname(__file__))


from bottle import get, default_app
from bottle import subprocess
from subprocess import Popen, PIPE
from bottle import response
from json import dumps

@get('/')
def main():
	rv = [{ "id": 1, "name": "Test Item 1" }, { "id": 2, "name": "Test Item 2" }]
	response.content_type = 'application/json'
	return dumps(rv)

#	return 'Main page'
#	return output

@get('/:name')
def main(name):
    return 'Page: ' + name

application = default_app()
