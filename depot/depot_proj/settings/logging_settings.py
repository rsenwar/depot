"""Logging settings."""

from django.utils.log import DEFAULT_LOGGING

# See: https://docs.djangoproject.com/en/dev/topics/logging/#filters
L_FILTERS = DEFAULT_LOGGING['filters'].copy()

# See: https://docs.djangoproject.com/en/dev/topics/logging/#formatters
L_FORMATTERS = {
    'all_details': {
        '()': 'lib.depot_logging.DepotFormatter',
        'format': '%(asctime)s %(levelname)s %(process)d|%(thread)d '
                  '%(name)s.%(funcName)s():%(lineno)d-> %(extra_msg)s %(message)s'
    },
    'depot_details': {
        '()': 'lib.depot_logging.DepotFormatter',
        'format': '%(asctime)s %(levelname)s %(process)d|%(thread)d '
                  '%(name)s.%(module)s.%(funcName)s():%(lineno)d-> %(extra_msg)s %(message)s'
    },
    'root_format': {
        'format': '%(asctime)s  %(levelname)s  %(name)s '
                  ' %(funcName)s %(message)s'
    },
    'simple': {
        'format': '%(asctime)s %(levelname)s %(message)s'
    },
    'console': {
        # exact format is not important, this is the minimum information
        'format': '%(asctime)s %(levelname)-8s %(name)-12s %(message)s',
    },
    'django.server': DEFAULT_LOGGING['formatters']['django.server'].copy(),
}

# See: https://docs.djangoproject.com/en/dev/topics/logging/#handlers
L_HANDLERS_DEV = {
    'default_handler': {
        # file-based
        'level': 'DEBUG',
        'formatter': 'all_details',
        'class': 'logging.FileHandler',
        'filename': '/logs/depot_apps.log',
    },
    'depot_handler': {
        # file-based
        'level': 'DEBUG',
        'formatter': 'depot_details',
        'class': 'logging.FileHandler',
        'filename': '/logs/depot_apps.log',
    },
    'stats_handler': {
        # file-based
        'level': 'ERROR',
        'formatter': 'all_details',
        'class': 'logging.FileHandler',
        'filename': '/logs/depot_apps_stats.log',
    },
    # 'sentry': {
    #     'level': 'ERROR',
    #     'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
    # },
    'mail_admins': {
        'level': 'ERROR',
        'class': 'django.utils.log.AdminEmailHandler',
        'filters': ['require_debug_false']
    },
    'null': {
        'class': 'logging.NullHandler',
    },
    'console': {
        'class': 'logging.StreamHandler',
        'filters': ['require_debug_true'],
        'formatter': 'console',
    },
    'django.server': DEFAULT_LOGGING['handlers']['django.server'],
}

L_HANDLERS_PROD = {
    'default_handler': {
        # file-based
        'level': 'INFO',
        'formatter': 'all_details',
        'class': 'logging.FileHandler',
        'filename': '/logs/depot_apps.log',
    },
    'depot_handler': {
        # file-based
        'level': 'INFO',
        'formatter': 'depot_details',
        'class': 'logging.FileHandler',
        'filename': '/logs/depot_apps.log',
    },
    'stats_handler': {
        # file-based
        'level': 'ERROR',
        'formatter': 'all_details',
        'class': 'logging.FileHandler',
        'filename': '/logs/depot_apps_stats.log',
    },
    # 'sentry': {
    #     'level': 'ERROR',
    #     'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
    # },
    'mail_admins': {
        'level': 'ERROR',
        'class': 'django.utils.log.AdminEmailHandler',
        'filters': ['require_debug_false']
    }
}

# See: https://docs.djangoproject.com/en/dev/topics/logging/#loggers
# The loggers have default level set at DEBUG on all environments. This will
# get filtered out at the handler level.
L_LOGGERS_PROD = {
    # root logger
    '': {
        'level': 'INFO',
        'handlers': ['default_handler'],
        'propagate': False,
    },
    'depot': {
        'handlers': ['depot_handler'],
        'level': 'INFO',
        'propagate': False,
    },
}

L_LOGGERS_DEV = {
    # root logger
    '': {
        'level': 'DEBUG',
        'handlers': ['default_handler'],
        'propagate': False,
    },
    'depot': {
        'handlers': ['depot_handler'],
        'level': 'DEBUG',
        'propagate': False,
    },
    'django.request': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': False,
    },
    'django': {
        'handlers': ['console'],
        'propagate': True,
    },
    'django.db.backends': {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': False,
    },

    'django.server': DEFAULT_LOGGING['loggers']['django.server'],
    'kafka': {
        'handlers': ['default_handler'],
        'level': 'DEBUG',
        'propagate': False,
    },
}
