"""Production settings for crystal project."""
# pylint: disable=unused-wildcard-import

from depot_proj.settings import base as base_settings
from depot_proj.settings.logging_settings import L_HANDLERS_PROD, L_LOGGERS_PROD, \
    L_FORMATTERS, L_FILTERS
from depot_proj.settings import settings_utility

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'q2kaummexhf3r0_%24%+nw^ts+49*@zjwacvs_@8r5uehupucu'


# calls to 3rd party should use prod/test/(mock?) APIs
API_TYPE = 'prod'

DEPOT_REDIS_HOST = 'depotredis.prod.goibibo.com'

# **********  ALLOWED_HOSTS **********************************
EC2_PRIVATE_IP = settings_utility.get_ec2_private_ip()

if EC2_PRIVATE_IP:
    ALLOWED_HOSTS = base_settings.ALLOWED_HOSTS + [EC2_PRIVATE_IP]
# ************************************************************

# ***** LOGGING CONFIGURATION

# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': L_FORMATTERS,     # noqa: F405
    'filters': L_FILTERS,           # noqa: F405
    'handlers': L_HANDLERS_PROD,    # noqa: F405
    'loggers': L_LOGGERS_PROD,
}
# ***** END LOGGING CONFIGURATION


# ***** DATABASE CONFIGURATION
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASE_ROUTERS = ['depot_proj.db_router.GoibiboApplicationRouter']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'depot',
        'USER': 'depot',
        'PASSWORD': 'depot',
        'HOST': 'goibibo.mysql.bbc.goibibo.com',
        # 'PORT': '',
        'CONN_MAX_AGE': 250,
        'OPTIONS': {
            "autocommit": True
        },
    },
    'goibibo_master': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'goibibo',
        'USER': 'gouser',
        'PASSWORD': 'g01b1b0',
        'HOST': 'goibibo.mysql.master.goibibo.com',
        # 'PORT': '',
        'CONN_MAX_AGE': 250,
        'OPTIONS': {
            "autocommit": True
        },
    },
    'goibibo_slave': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'goibibo',
        'USER': 'gouser',
        'PASSWORD': 'g01b1b0',
        'HOST': 'goibibo.mysql.slave.goibibo.com',
        # 'PORT': '',
        'CONN_MAX_AGE': 250,
        'OPTIONS': {
            "autocommit": True
        },
    }

}
# ***** END DATABASE CONFIGURATION

