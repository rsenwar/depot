"""Hotels Models helpers."""

import logging

from apps.app_helpers import utility
from lib import smartjson

# import copy
# import time

logger = logging.getLogger(__name__)


def get_bookjson_as_python_dict(model_obj):     # noqa: C901
    """Return bookjson as dict.

    Args:
        model_obj: booking model object

    Returns:
        (dict)

    """
    bjs = {}
    try:
        if model_obj.bookjson:
            bjs = smartjson.loads(model_obj.bookjson)
    except ValueError as ex:
        logger.critical("%s\t%s", "get_bookjson_as_python_dict", ex, exc_info=True)

    return bjs


def get_farebreakup_as_python_dict(model_obj):
    """Return farebreakup as dict.

    Args:
        model_obj: booking model object

    Returns:

    """
    fb = {}
    if model_obj.farebreakup:
        fb = model_obj.farebreakup.strip()
    if fb:
        fb = utility.convert_json_into_dict(fb)

    if isinstance(fb, dict) is False:
        fb = {}

    return fb

