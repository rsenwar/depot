"""Multiple Database Router."""
from django.conf import settings

env_name = settings.ENVIRONMENT_NAME

NO_WRITE_MODELS = {'user', 'customuserprofile', 'customsite', 'customcontenttype'}


class GoibiboApplicationRouter:
    """Goibibo Database Router.

    A router to control all database operations on models in the Goibibo
    Application.
    """

    @staticmethod
    def db_for_read(model, **hints):
        """Return db for read."""
        if model._meta.app_label in ['goibibo']:
            db_name = 'goibibo_slave'
        else:
            db_name = 'default'
        return db_name

    @staticmethod
    def db_for_write(model, **hints):
        """Return db for write."""
        if model._meta.app_label == 'goibibo':
            if model._meta.model_name in NO_WRITE_MODELS:
                raise Exception('write not allowed here')
            db_name = 'goibibo_master'
        else:
            db_name = 'default'
        return db_name

    @staticmethod
    def allow_migrate(db, app_label, model_name=None, **hints):
        """Return flag to allow migrations."""
        if app_label in ['goibibo']:
            val = False
        else:
            val = True
        return val

    @staticmethod
    def allow_relation(obj1, obj2, **hints):
        """Return flag to allow replica."""
        # pylint: disable=protected-access
        db_list = ('goibibo_master', 'goibibo_slave')
        val = None
        if obj1._state.db in db_list and obj2._state.db in db_list:
            val = True
        return val


class ApplicationTestRouter:
    """Test Router.

    A test router to control all database operations on models in the Goibibo
    Application.

    """

    @staticmethod
    def db_for_read(model, **hints):
        """Return db for read."""
        if model._meta.app_label in ['goibibo']:
            db_name = 'goibibo_master'
        else:
            db_name = 'default'
        return db_name

    @staticmethod
    def db_for_write(model, **hints):
        """Return db for write."""
        if model._meta.app_label == 'goibibo':
            if env_name != 'test' and model._meta.model_name in NO_WRITE_MODELS:
                raise Exception('write not allowed here')
            db_name = 'goibibo_master'
        else:
            db_name = 'default'
        return db_name

    @staticmethod
    def allow_migrate(db, app_label, model_name=None, **hints):
        """Return flag to allow migrations."""
        if app_label in ['goibibo']:
            val = False
        else:
            val = True
        return val

    @staticmethod
    def allow_relation(obj1, obj2, **hints):
        """Return flag to allow replica."""
        # pylint: disable=protected-access
        db_list = ('goibibo_master', 'goibibo_slave')
        val = None
        if obj1._state.db in db_list and obj2._state.db in db_list:
            val = True
        return val
