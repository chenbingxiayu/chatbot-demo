#!/bin/bash

celery flower -A chatbot_demo --port=5555 --broker=redis://localhost:6379/0
