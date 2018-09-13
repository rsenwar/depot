"""Cache helper classes and methods."""
from threading import Lock

from django.utils.encoding import smart_str
from django_redis import get_redis_connection

# from django.core.cache import cache

__all__ = ['RedisCacheClass', ]


def make_cachekey(key, key_prefix, version):
    """Make cache key."""
    return smart_str(key)


class RedisCacheClass(object):
    """Redis Cache Class.

    Examples:
        >>> voyager_rdis_client = RedisCacheClass.get_voyager_redis_client()
        >>> voyager_rdis_cli_pipe = RedisCacheClass.get_voyager_redis_cli_pipeline()

    """

    _rdis = None

    def __init__(self):
        """Initialize class RedisCacheClass."""
        pass

