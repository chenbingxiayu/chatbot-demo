#!/bin/bash

set -a
source ../.env.docker
set +a

if [[ "$1" == 'createsuperuser' ]]; then
  python manage.py createsuperuser --no-input --netid=admin
else
  python manage.py "$@"
fi
read -rsp $'\nPress enter to exit...\n'
