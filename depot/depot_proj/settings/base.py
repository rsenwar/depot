"""
Django settings for depot_proj project.

Generated by 'django-admin startproject' using Django 2.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'q2kaummexhf3r0_%24%+nw^ts+49*@zjwacvs_@8r5uehupucu'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['depot.goibibo.com',
                 'depot.local.goibibo.com',
                 'depot.dev.goibibo.com'
                 ]
# ***** APP CONFIGURATION
# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'rest_framework',  # rest framework
    'rest_framework.authtoken',
    'rest_framework_swagger',
]

LOCAL_APPS = [
]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
# ***** END APP CONFIGURATION


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'depot_proj.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'depot_proj.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASE_ROUTERS = ['depot_proj.db_router.GoibiboApplicationRouter']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'depot',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': ''
    },
    'goibibo_master': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'travelibibo',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': ''
    },
    'goibibo_slave': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'travelibibo',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': ''
    }

}
# ***** END DATABASE CONFIGURATION



# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = '/var/www/depot/static/'
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, "www/static"),
]

API_TYPE = 'test'

FLAVOURS = {'v2', 'v3', 'ios', 'android', 'mobile', 'win8', 'winph', 'full'}

SITE_ID = 1
SESSION_COOKIE_DOMAIN = '.depot.goibibo.com'
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# ***** HOST CONFIGURATION
GOIBIBO_HOST = 'https://www.goibibo.com'
GOCASH_HOST = 'https://gocash.goibibo.com'
VOYAGER_HOST = 'https://voyager.goibibo.com'


# ***** REST FRAMEWORK CONFIGURATION
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    # ],
    # 'DEFAULT_AUTHENTICATION_CLASSES': (
    #     'rest_framework.authentication.BasicAuthentication',
    #     'rest_framework.authentication.SessionAuthentication',
    # ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    # 'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'TEST_REQUEST_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.MultiPartRenderer',
        'rest_framework.renderers.TemplateHTMLRenderer'
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}
# ***** END REST FRAMEWORK CONFIGURATION

# ***** CACHES CONFIGURATION
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'KEY_FUNCTION': 'apps.app_helpers.cache_helper.make_cachekey',
        'OPTIONS': {
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            # "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
        }
    }

}

# ***** END CACHES CONFIGURATION
LOGGING_CONFIG = None
from django.utils.log import DEFAULT_LOGGING    # pylint: disable=wrong-import-position
from lib import smartlogging    # pylint: disable=wrong-import-position

# ***** LOGGING CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/topics/logging/#filters

L_FILTERS = DEFAULT_LOGGING['filters']

# See: https://docs.djangoproject.com/en/dev/topics/logging/#formatters
L_FORMATTERS = {
    'all_details': {
        'format': '%(asctime)s %(levelname)s %(process)d|%(thread)d '
                  '%(name)s.%(funcName)s():%(lineno)d %(message)s'
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
    'django.server': DEFAULT_LOGGING['formatters']['django.server'],
}

# See: https://docs.djangoproject.com/en/dev/topics/logging/#handlers
L_HANDLERS = {
    'default_handler': {
        # file-based
        'level': 'INFO',
        'formatter': 'all_details',
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
        'filters': ['require_debug_true']
    },
    'null': {
        'class': 'logging.NullHandler',
    },
    'console': {
        'class': 'logging.StreamHandler',
        'formatter': 'console',
    },
    'django.server': DEFAULT_LOGGING['handlers']['django.server'],
}

L_ACTIVE_HANDLERS = [
    'default_handler', 'stats_handler',
]

# See: https://docs.djangoproject.com/en/dev/topics/logging/#loggers
# The loggers have default level set at DEBUG on all environments. This will
# get filtered out at the handler level.

# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# ***** END LOGGING CONFIGURATION
