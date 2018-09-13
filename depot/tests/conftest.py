# from django.conf import settings

# def pytest_configure():
#     settings.configure()

import os
import sys

import pytest
from django.conf import settings
from django.core.management import call_command

PROJECT_DIR = settings.PROJECT_ROOT
DB_FILES_LOCATION = settings.PROJECT_ROOT + '/data/'
sys.path.append(os.path.dirname(__file__))


@pytest.fixture(scope='session')
def django_db_setup(django_db_keepdb, django_db_blocker):
    import pdb; pdb.set_trace()
    from pytest_django.fixtures import _disable_native_migrations
    _disable_native_migrations()
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DB_FILES_LOCATION, 'depot.sqlite3'),
    }
    settings.DATABASES['goibibo_master'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DB_FILES_LOCATION, 'travelibibo.sqlite3'),
    }
    settings.DATABASES['goibibo_slave'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DB_FILES_LOCATION, 'travelibibo.sqlite3'),
    }
    with django_db_blocker.unblock():
        call_command('loaddata', '--database', 'default', 'django_data.json')
        call_command('loaddata', '--database', 'goibibo_master', 'custom_models.json')
                     # 'custom_content_types.json', 'bus_models.json')



@pytest.fixture(scope='session')
def django_db_modify_db_settings():
    pass


# @pytest.fixture(autouse=True)
# def no_requests(monkeypatch):
#     monkeypatch.delattr("requests.sessions.Session.request")

# @pytest.fixture(scope='function')
# def get_markers(request):
#     print([marker.name for marker in request.function.pytestmark])

def pytest_report_header(config):
    """Pytest report Header."""
    return "Depot Project"
