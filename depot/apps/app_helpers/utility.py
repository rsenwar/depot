"""Common utility functions."""
import ast
import copy
import decimal
import logging

import dateutil.parser as date_parser

from lib import smartjson

logger = logging.getLogger(__name__)


def display_numbers(num):
    """Return number as human readable format.

    Args:
        num: (int/float)

    Returns:
        (string)

    Examples:
        >>> display_numbers(1000)
        1,000
        >>> display_numbers(12123.4)
        12,123.40

    """
    if isinstance(num, int):
        val = '{:,}'.format(num)
    elif isinstance(num, float):
        val = '{:,.2f}'.format(num)
    elif isinstance(num, decimal.Decimal):
        val = num.quantize(decimal.Decimal('0.00')).to_eng_string()
    else:
        val = str(num)
    return val


def get_iso8601_format(input_string):
    """Return iso 8601 datetime format.

    Args:
        input_string:

    Returns:

    Examples:
        >>> input_string = 'Thu, 16 Dec 2010 12:14:05 +0000'
        >>> get_iso8601_format(input_string)
        "2010-12-16T12:14:05+00:00"

    """
    input_date = date_parser.parse(input_string)
    return input_date.isoformat()


def convert_json_into_dict(data):
    """Convert json string into python dict.

    Args:
        data:

    Returns:

    """
    if not isinstance(data, dict):
        try:
            data = smartjson.loads(data)
        except Exception as ex:
            logger.debug("%s\t%s", "json_loads", ex)

    if not isinstance(data, dict):
        try:
            data = ast.literal_eval(data)
        except Exception as ex:
            logger.debug("%s\t%s", "literal_eval", ex)

    return data
