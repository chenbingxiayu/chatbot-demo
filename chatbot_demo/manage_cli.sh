#!/bin/bash

set -a
source ../.env
set +a

export MYSQL_HOST=127.0.0.1

if [[ "$1" == 'createsuperuser' ]]; then
  python manage.py createsuperuser --no-input --netid=admin
else
  python manage.py "$@"
fi
read -rsp $'\nPress enter to exit...\n'
