import time
from functools import wraps
from lib import smartlogging

logger = smartlogging.getLogger("depot")


def timed_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        start = time.time()
        result = f(*args, **kwds)
        elapsed = (time.time() - start)*1000
        logger.debug("f::{0} t::{1:0.2f} ms".format(f.__name__, elapsed))
        return result
    return wrapper
