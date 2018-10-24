# pylint: disable=unused-wildcard-import
import os
from depot_proj.settings.base import *    # pylint: disable:wildcard-import
from depot_proj.settings.logging_settings import L_HANDLERS_DEV, L_LOGGERS_DEV, \
    L_FORMATTERS, L_FILTERS

DEBUG = True
SITE_ID = 1
INTERNAL_IPS = ['127.0.0.1', ]
API_TYPE = 'test'
ENVIRONMENT_NAME = "dev"
HOST_NAME = '127.0.0.1'
LOCAL_HOST = 'host.docker.internal'
GOIBIBO_HOST = 'http://depot.local.goibibo.com:8009'
GOCASH_HOST = 'http://depot.local.goibibo.com:8081'
VOYAGER_HOST = 'http://voyager.goibibo.com'
ALLOWED_HOSTS = ['.' + HOST_NAME, '.' + HOST_NAME + '.',]
SESSION_COOKIE_DOMAIN = '.depot.local.goibibo.com'
PORT = os.environ.get("RUN_PORT", '8009')
if PORT:
    HOST = '{}:{}'.format(HOST_NAME, PORT)
else:
    HOST = HOST_NAME

MEDIA_URL = 'http://{}/static/'.format(HOST)

INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar',
]

if 'debug_toolbar' in INSTALLED_APPS:
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]

# LOCAL_HOST = 'localhost'
DEPOT_REDIS_HOST = LOCAL_HOST

DB_FILES_LOCATION = PROJECT_ROOT + '/data/'
DATABASES1 = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'depot',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'LOCAL_HOST',
        'PORT': ''
    },
    'goibibo_master': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'travelibibo',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'LOCAL_HOST',
        'PORT': ''
    },
    'goibibo_slave': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'travelibibo',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'LOCAL_HOST',
        'PORT': ''
    }

}

DATABASES={
        'default':{
                'NAME':'goibibo',
                'ENGINE':'django.db.backends.mysql',
                'USER':'gouser',
                'PASSWORD':'g01b1b0',
                'HOST':'10.70.15.104',
                'PORT':'',
                'CONN_MAX_AGE': 60,
#                'OPTIONS':{"autocommit": True},
                },
        'slave':{
                 'NAME':'goibibo',
                 'ENGINE':'django.db.backends.mysql',
                 'USER':'gouser',
                 'PASSWORD':'g01b1b0',
                 'HOST':'10.70.15.104',
                 'PORT':'',
                 'CONN_MAX_AGE': 60,
#                 'OPTIONS':{"autocommit": True},
                 'TEST_MIRROR': 'default'
                },
        'stats':{
                 'NAME':'stats',
                 'ENGINE':'django.db.backends.mysql',
                 'USER':'goibibo',
                 'PASSWORD':'goibibo123',
                 'HOST':'10.70.46.43',
                 'PORT':'3306',
                 'CONN_MAX_AGE': 60,
                 'OPTIONS':{"autocommit": True},
                 'TEST_MIRROR':'default'
                },
        'report': {
                'NAME': 'goibibo',
                'ENGINE': 'django.db.backends.mysql',
                'USER': 'goibibo',
                'PASSWORD': 'goibibo123',
                'HOST': 'localhost',
                'PORT': ''
               },
        'travelb2b':{
                'NAME': 'travelb2b',
                'ENGINE': 'django.db.backends.mysql',
                'USER': 'phoenix',
                'PASSWORD': 'phoenix#1',
                'HOST': '10.70.15.104',
                'PORT': '3306',
                'OPTIONS': {
                        "init_command": "SET storage_engine=INNODB"
                }
        }
}


# ***** LOGGING CONFIGURATION
LOGGING_CONFIG = None
from django.utils.log import DEFAULT_LOGGING
from lib import smartlogging

L_LOGGERS = {
    # root logger
    '': {
        'level': 'DEBUG',
        'handlers': ['default_handler'],
        'propagate': False,
    },
    'depot': {
        'handlers': ['default_handler'],
        'level': 'DEBUG',
        'propagate': False,
    },
    'django.request': {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': False,
    },
    'django': {
        'handlers': ['console'],
        'propagate': False,
    },

    'django.server': DEFAULT_LOGGING['loggers']['django.server']

}
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# ***** END LOGGING CONFIGURATION

# Cache Settings
'''
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://%s/1' % LOCAL_HOST,
        'KEY_FUNCTION': 'apps.app_helpers.cache_helper.make_cachekey',
        'OPTIONS': {
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            # "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
        }
    }
}
'''
# rest framework settings

# ***** LOGGING CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': L_FORMATTERS,     # noqa: F405
    'filters': L_FILTERS,           # noqa: F405
    'handlers': L_HANDLERS_DEV,         # noqa: F405
    'loggers': L_LOGGERS_DEV,
}
# ***** END LOGGING CONFIGURATION

# Cache Settings
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://%s/1' % DEPOT_REDIS_HOST,
        'KEY_FUNCTION': 'apps.app_helpers.cache_helper.make_cachekey',
        'OPTIONS': {
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            # "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
        }
    },
    'hotel_voyager_data': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://%s/2' % DEPOT_REDIS_HOST,
        'KEY_FUNCTION': 'apps.app_helpers.cache_helper.make_cachekey',
        'TIMEOUT': 24 * 60 * 60,
        'OPTIONS': {
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            # "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
        }
    }
}
# END Cache Settings

# session settings
SESSION_COOKIE_DOMAIN = '.depot.local.goibibo.com'
SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS = {
    'host': DEPOT_REDIS_HOST,
    'port': 6379,
    'db': 4,
    'prefix': 'session',
    'socket_timeout': 1
}
# end session settings

# *********** CELERY CONFIGURATION ********************************
CELERY_BROKER_URL = "redis://%s:6379/7" % DEPOT_REDIS_HOST
CELERY_RESULT_BACKEND = "redis://%s:6379/7" % DEPOT_REDIS_HOST
# *********** END CELERY CONFIGURATION ****************************

# rest framework settings

# DEBUG TOOLBAR Settings:
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]
DEBUG_TOOLBAR_CONFIG = {
    'PROFILER_MAX_DEPTH': 25
}
