"""Service Configs for base API structure."""

API_HOST = {
    'prod': {'host': ''},
    'test': {'host': ''},
    'pp': {'host': ''},
    'dev': {'host': ''},
    'prodpp': {'host': ''},
}

API_ACTION_MAP = {
    'some_action': {'path': '/path1/destination1/', 'method': 'GET'}
}

SERVICE_CONNECTIONS = {
    'NO_OF_SERVICES': 15,
    'NO_OF_POOLS': 1,
    'POOL_MAX_SIZE': 10
}

DEFAULT_TIMEOUT = 300
