#!/bin/bash

REDIS_HOST="${REDIS_HOST:=localhost}"
REDIS_PORT="${REDIS_HOST:=6379}"

flower --port=5555 --broker=redis://$REDIS_HOST:$REDIS_PORT/0
