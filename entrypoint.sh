#!/bin/sh

python -m gunicorn \
  --bind=0.0.0.0:8000 \
  --access-logfile - \
  -k gevent \
  --workers=1 \
  app
