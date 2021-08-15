#!/bin/bash

if [ -z "$REDIS_HOST" ]; then
  echo "Read env variables from .env"
  set -a
  source ../.env
  set +a
else
  echo "Run in containerized environment"
fi

rm celerybeat*
celery -A chatbot_demo beat -l info