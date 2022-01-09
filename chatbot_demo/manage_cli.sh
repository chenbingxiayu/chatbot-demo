#!/bin/bash

# Load environment variables
set -a
source ../.env.docker
set +a

#export MYSQL_HOST=localhost

# Clear cache in migration dir
find main/migrations -type f -name "*.pyc" -delete

if [[ "$1" == 'createsuperuser' ]]; then
  python3 manage.py createsuperuser --netid=admin
else
  python3 manage.py "$@"
fi
read -rsp $'\nPress enter to exit...\n'
