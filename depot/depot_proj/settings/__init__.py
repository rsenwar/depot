"""Depot Project Settings."""
# pylint: disable=wildcard-import

import os

from .base import *

ENVIRONMENT_NAME = os.environ.setdefault('CURR_ENV', 'PROD').lower()


try:
    if ENVIRONMENT_NAME == 'dev':
        from .dev import *

    elif ENVIRONMENT_NAME == 'pp':
        from .pp import *

    elif ENVIRONMENT_NAME == 'prodpp':
        from .prodpp import *

    elif ENVIRONMENT_NAME == 'prod':
        from .production import *

    elif ENVIRONMENT_NAME == 'test':
        from .test_settings import *

    else:
        from .local import *

except Exception:
    pass
