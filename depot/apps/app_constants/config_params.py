"""Config params(Database).

USAGE:
-------
>>> from apps.app_constants.config_params import bus_config_params
>>> from apps.app_constants import bus_contansts
>>> CONFIG_VALUE = bus_config_params.CONFIG_KEY
>>> if CONFIG_VALUE is None:
>>>     CONFIG_VALUE = bus_contansts.CONFIG_KEY

"""

import copy
import logging
import time

from django.conf import settings

from apps.goibibo.models import busConfigParam as ConfigParam

__all__ = ['bus_config_params', ]
logger = logging.getLogger(__name__)

ENVIRONMENT_TYPE_MAP = {
    'dev': 1,
    'pp': 4,
    'prop': 2,
    'prodpp': 3
}
NEW_FETCH_PERIOD = 1 * 60


class BusDbConfigParams(object):
    """Hotel DB Configs."""

    _bus_config_params = {}
    _last_refresh_time = None
    _fetch_new = True

    def __init__(self):
        """Initialize HotelDbConfigParams."""
        pass

    def __getattr__(self, item):
        """Get attribute."""
        return self.get(item)

    def _should_refresh(self):
        """Check the condition to refresh the data."""
        current_timestamp = time.time()
        if not self._bus_config_params:
            val = True
        elif not self._last_refresh_time:
            val = True
        elif (current_timestamp - self._last_refresh_time) > NEW_FETCH_PERIOD:
            val = True
        else:
            val = False
        return val

    def get(self, item, default_value=None):
        """Get the item from db or memory."""
        if self._should_refresh():
            self._fetch_new = True
            self._fetch_config_params()

        config_params = self._bus_config_params
        return config_params.get(item, default_value)

    @staticmethod
    def _fetch_config_params():
        """Fetch config params."""
        config_params = {}
        try:
            config_params = BusDbConfigParams._bus_config_params
            if BusDbConfigParams._fetch_new:
                config_params = BusDbConfigParams._fetch_config_params_from_db()
                if config_params:
                    BusDbConfigParams._hotel_config_params = config_params
                    BusDbConfigParams._last_refresh_time = time.time()
                    BusDbConfigParams._fetch_new = False

        except Exception as ex:
            logger.exception("%s", str(ex))

        return config_params

    @staticmethod
    def _fetch_config_params_from_db():
        """Fetch config params from the DB."""
        env_name = getattr(settings, 'ENVIRONMENT_NAME', 'prod').lower()
        env_type = ENVIRONMENT_TYPE_MAP.get(env_name, 2)
        config_params = {}
        try:
            cp_obj_list = ConfigParam.objects \
                .values_list('config_key', 'config_value')\
                .filter(active=True, environment_type=env_type)

            if cp_obj_list:
                config_params = dict(cp_obj_list)

            # to overwrite missing keys in prodpp mode
            if env_name not in ['prodpp', 'pp', 'dev']:
                cp_obj_list_prod = ConfigParam.objects \
                    .values_list('config_key', 'config_value') \
                    .filter(active=True, environment_type=2)

                if cp_obj_list_prod:
                    config_prod = dict(cp_obj_list_prod)
                    config_prod.update(config_params)
                    config_params = copy.deepcopy(config_prod)
        except Exception as ex:
            logger.exception("%s", str(ex))

        return config_params


bus_config_params = BusDbConfigParams()
