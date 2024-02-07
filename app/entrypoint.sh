#!/bin/bash

gunicorn main:app --workers 5 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8085 --forwarded-allow-ips='*'
