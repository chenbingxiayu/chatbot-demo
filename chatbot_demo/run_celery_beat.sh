#!/bin/bash

set -a
source .env
set +a

rm celerybeat*
celery -A chatbot_demo beat -l info