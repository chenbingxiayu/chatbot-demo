#!/bin/bash

set -a
source ../.env.docker
set +a

#export MYSQL_HOST=localhost

if [[ "$1" == 'createsuperuser' ]]; then
  python manage.py createsuperuser --netid=admin
else
  python manage.py "$@"
fi
read -rsp $'\nPress enter to exit...\n'
