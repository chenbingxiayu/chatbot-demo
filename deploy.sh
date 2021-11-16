#!/bin/bash


cd chatbot_demo
echo -e "\nRemove old main-*js files"
rm -v main/static/main-*.js
npm run prod

cd ..
echo -e "\nDeploy backend\n"
docker-compose up -d --build django celery celery_beat