import os

from celery import Celery as _Celery
from django.apps import AppConfig

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'depot_proj.settings')

app = _Celery('celery_app')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Make Dummy Task."""
    print('Request: {0!r}'.format(self.request))


class CeleryAppConfig(AppConfig):
    """Celery app config."""

    name = 'celery_app'
