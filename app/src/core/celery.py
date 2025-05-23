import logging
import os

from celery import Celery
from celery.signals import setup_logging, worker_process_shutdown
from django.conf import settings
from django_structlog.celery.steps import DjangoStructLogInitStep

from prometheus_client import multiprocess


from .settings import configure_structlog

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.steps["worker"].add(DjangoStructLogInitStep)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@setup_logging.connect
def receiver_setup_logging(loglevel, logfile, format, colorize, **kwargs):  # pragma: no cover
    config = settings.LOGGING
    # worker and master have a logfile, beat does not
    if logfile:
        config["handlers"]["console"]["class"] = "logging.FileHandler"
        config["handlers"]["console"]["filename"] = logfile
    logging.config.dictConfig(config)
    configure_structlog()


def route_task(name, args, kwargs, options, task=None, **kw):
    return {"queue": "celery"}



@worker_process_shutdown.connect
def child_exit(pid, **kw):
    multiprocess.mark_process_dead(pid)

