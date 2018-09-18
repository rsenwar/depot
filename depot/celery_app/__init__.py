"""Celery App."""

# pylint: disable=wrong-import-position
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "depot_proj.settings")
# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.

from celery_app.apps import app as celery_app
