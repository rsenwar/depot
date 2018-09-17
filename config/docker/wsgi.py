"""
WSGI config for depot project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from newrelic import agent as newrelic_agent


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "depot_proj.settings")

newrelic_agent.initialize('/etc/newrelic/newrelic_depot.ini')

application = get_wsgi_application()

