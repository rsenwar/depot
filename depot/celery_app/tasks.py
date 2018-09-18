"""Depot Project Tasks."""
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def add(x=5, y=7):
    """Add two numbers."""
    z = 0
    try:
        z = x + y
        logger.info("tasks add return %s", z)
    except Exception as ex:
        logger.critical("tasks exception %s", ex)

    return z
