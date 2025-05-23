#!/bin/sh

# We assume that WORKDIR is defined in Dockerfile
export PYTHONPATH=/app/app/src

/app/app/prometheus-cleanup.sh

# django-probes
uv run /app/app/src/manage.py wait_for_database --timeout 10

# this seems to be the only place to put this for AWS deployments to pick it up
uv run /app/app/src/manage.py migrate

gunicorn -c /app/app/gunicorn.conf.py
