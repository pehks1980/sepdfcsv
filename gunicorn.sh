#!/bin/sh

# Check if FLASK_SECRET_KEY environment variable is set
if [ -z "$FLASK_SECRET_KEY" ]; then
    echo "ERROR: FLASK_SECRET_KEY environment variable is not set. Please set the secret key and try again."
    exit 1
fi

#run memcached as daemon under user
#memcached -u user -d
/cache-serv/main &
gunicorn --chdir main main:app -w 2 --threads 2 -b 0.0.0.0:8080 --access-logfile '-'
