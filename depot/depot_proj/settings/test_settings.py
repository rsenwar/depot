"""Test settings for crystal project."""
# pylint: disable=unused-wildcard-import
import os
from depot_proj.settings.base import *    # noqa: F403 pylint: disable=wildcard-import

os.environ.setdefault('CURR_ENV', 'test')

ENVIRONMENT_NAME = 'test'
API_TYPE = 'test'
DB_FILES_LOCATION = PROJECT_ROOT + '/data/'     # noqa: F405
SITE_ID = 1


INSTALLED_APPS += [     # noqa: F405
    'apps.goibibo',
]
LOCAL_HOST = 'localhost'
HOST_NAME = 'depot.local.goibibo.com'
PORT = os.environ.get("RUN_PORT", '8009')
if PORT:
    HOST = '{}:{}'.format(HOST_NAME, PORT)
else:
    HOST = HOST_NAME

DATABASE_ROUTERS = ['depot_proj.db_router.ApplicationTestRouter']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DB_FILES_LOCATION, 'depot.sqlite3'),
        'TEST': {
            'NAME': os.path.join(DB_FILES_LOCATION, 'depot.sqlite3'),
        }
    },
    'goibibo_master': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DB_FILES_LOCATION, 'travelibibo.sqlite3'),
        'TEST': {
            'NAME': os.path.join(DB_FILES_LOCATION, 'travelibibo.sqlite3'),
        }
    },
    'goibibo_slave': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DB_FILES_LOCATION, 'travelibibo.sqlite3'),
        'TEST': {
            'MIRROR': 'goibibo_master'
        }
    },
}

# ***** MIDDLEWARE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
# ***** END MIDDLEWARE CONFIGURATION

# **********   KAFKA CONFIGURATION ********************************
KAFKA_BROKERS = '%s:9092' % LOCAL_HOST

# ***********   END KAFKA CONFIGURATION ***************************


# *************** FIXTURE CONFIGURATION **************************************
#FIXTURE_DIRS = [
#    PROJECT_ROOT + '/data/fixtures/',   # noqa: F405
#]
FIXTURE_DIRS = (
    os.path.join(PROJECT_ROOT, "data/fixtures/", ),
)

# *************** END FIXTURE CONFIGURATION **********************************

USE_TZ = False



