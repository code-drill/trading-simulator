#!/bin/sh
set -eu

export PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus-multiproc-dir
export PYTHONPATH=/app/app/src
export PYTHONUNBUFFERED=true

/app/app/prometheus-cleanup.sh

celery -A core worker -l INFO -c 1 --pidfile=/tmp/celery-%n.pid
