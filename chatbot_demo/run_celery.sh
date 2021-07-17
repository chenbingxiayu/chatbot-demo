#!/bin/bash

set -a
source .env
set +a

celery -A chatbot_demo worker -l info -P gevent -n worker1.%h
