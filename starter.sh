#!/bin/bash

uwsgi_python27 --socket 127.0.0.1:3333 --file /home/timofey/works/code/python/venv/index.wsgi --touch-reload=/home/timofey/works/code/python/venv/index.wsgi --chdir /home/timofey/works/code/python/venv -p 2 --threads 5 -b 8192
