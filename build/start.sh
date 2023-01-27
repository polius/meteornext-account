#!/bin/sh
cd /root
gunicorn --worker-class gthread --workers 1 --threads 100 --bind unix:server.sock --log-file error.log --daemon app:app
nginx -g 'daemon off;'