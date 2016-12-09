#!/bin/bash

uwsgi_python27 --socket 127.0.0.1:4444 --file /home/test/glacier/python_glacier/index.wsgi --touch-reload=/home/test/glacier/python_glacier/index.wsgi --chdir /home/test/glacier/python_glacier/ -p 2 --threads 5 -b 8192
