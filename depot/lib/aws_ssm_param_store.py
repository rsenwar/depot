"""
    Auto refreshing AWS SSM PARAMETER STORE API

USAGE:
-------
from lib.aws_ssm_param_store import SSMParameterStore
ssm_store = SSMParameterStore.get_instance()
PARAM_VALUE = ssm_store.get("PARAMETER NAME")

"""


import time
from threading import Lock

import boto3

from lib import smartjson

MAX_AGE = 10    # seconds
MAX_BATCH_SIZE = 10

SSM_CLIENT_LOCK = Lock()


class SSMParameterStore(object):
    # Here will be the instance stored.
    _instance = None
    _ssm_client = None
    _last_refresh_time = None
    _values = {}
    _parameters = set()

    def __init__(self, with_decryption=True):
        if SSMParameterStore._instance is not None:
            raise Exception("Init is not allowed :(")
        else:
            SSMParameterStore._instance = self
        self._max_age = MAX_AGE
        self._with_decryption = with_decryption

    @staticmethod
    def get_instance():
        """ static access method."""
        if SSMParameterStore._instance is None:
            with SSM_CLIENT_LOCK:
                if SSMParameterStore._instance is None:
                    SSMParameterStore._instance = SSMParameterStore()
        return SSMParameterStore._instance

    def set_ssm_client(self, client):
        """Override the default boto3 SSM client with your own."""
        if not hasattr(client, 'get_parameters'):
            raise TypeError('client must have a get_parameters method')
        if not hasattr(client, 'get_parameter'):
            raise TypeError('client must have a get_parameter method')
        self._ssm_client = client

    def _get_ssm_client(self):
        if self._ssm_client is None:
            self._ssm_client = boto3.client('ssm')
        return self._ssm_client

    def _should_refresh(self):
        # never force refresh if no max_age is configured
        if not self._max_age:
            val = False
        # always force refresh if values were never fetched
        elif not self._last_refresh_time:
            val = True
        else:
            # force refresh only if max_age seconds have expired
            val = time.time() - self._last_refresh_time > self._max_age
        return val

    def refresh(self):
        """ Updates the value(s) of this refreshable """
        names = list(self._parameters)
        values, invalid_names = self._get_parameters(names, self._with_decryption)
        if invalid_names:
            self._parameters = self._parameters - set(invalid_names)
            # todo: sent to newrelic
        self._values = values

        # keep track of update date for max_age checks
        self._last_refresh_time = time.time()

    @staticmethod
    def _batch(iterable, batch_size):
        """
        Turn an iterable into an iterable of batches of size n (or less, for the last one)

        """
        length = len(iterable)
        for ndx in range(0, length, batch_size):
            yield iterable[ndx:min(ndx + batch_size, length)]

    def _get_parameters(self, names, with_decryption):
        values = {}
        invalid_names = []
        for name_batch in self._batch(names, MAX_BATCH_SIZE):
            # can only get 10 parameters at a time
            print("About to get the value from store")
            response = self._get_ssm_client().get_parameters(
                Names=list(name_batch),
                WithDecryption=with_decryption,
            )
            invalid_names.extend(response['InvalidParameters'])
            for item in response['Parameters']:
                values[item['Name']] = item['Value']
                if item['Type'] == 'StringList':
                    values[item['Name']] = item['Value'].split(',')
            print("Fetched value from store")
        return values, invalid_names

    def _get_parameter(self, name, with_decryption):
        response = self._get_ssm_client().get_parameter(
            Name=name, WithDecryption=with_decryption)
        if 'Parameter' in response:
            item = response['Parameter']
            self._values[item['Name']] = item['Value']
            if item['Type'] == 'StringList':
                self._values[item['Name']] = item['Value'].split(',')

        val = self._values.get(name)
        return val

    def get(self, param_name, default_value=None):
        self._parameters.add(param_name)
        if self._should_refresh():
            self.refresh()

        if param_name not in self._values:
            val = self._get_parameter(param_name, self._with_decryption)
        else:
            val = self._values.get(param_name)

        if val:
            val = self._format_value(val)
        return val

    @staticmethod
    def _format_value(value):
        val = value
        if isinstance(value, str):
            try:
                val = smartjson.loads(value)
                if isinstance(val, (int, float)):
                    val = value
            except (ValueError, KeyError):
                val = value

        return val
