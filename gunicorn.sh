#!/bin/sh
#run memcached as daemon under user
#memcached -u user -d
/cache-serv/main &
gunicorn --chdir main main:app -w 2 --threads 2 -b 0.0.0.0:8080 --access-logfile '-'
