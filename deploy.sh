#!/bin/bash

cd chatbot_demo
npm run prod

cd ..
docker-compose up -d --build django celery celery_beat