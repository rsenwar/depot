# -*- coding: utf-8 -*-
"""Base service API structure. for calling requests and app_settings."""
# import copy
# import gzip
import hashlib
import hmac
import logging
# import io
import uuid
from collections import OrderedDict
from urllib import parse as urllib_parse
import requests
from requests.adapters import HTTPAdapter
from django.conf import settings
from dict_to_proto3_to_dict.dict_to_proto3_to_dict import dict_to_protobuf, protobuf_to_dict

from apps.services.service_base import service_configs
from lib import smartjson


class ServiceBase(object):
    """A base for all services."""

    _session = None

    def __init__(self, action_id, opts=None):
        """Initialize class ServiceBase."""
        self.track_id = uuid.uuid4().hex
        self.api_type = settings.API_TYPE
        self.env_type = settings.ENVIRONMENT_NAME
        self.options = {}
        if opts:
            self.options = opts.copy()
        self.service_host = ''
        self.proxy = ''
        self.proxy_port = 0
        self.proxies = {}
        self.username = ''
        self.password = ''
        self.request_url = ''
        self.http_method = 'GET'
        self.action_id = action_id
        self.action_path = ''
        self.resp = {'success': False, 'data': None, 'message': '',
                     'datafrom': self.__class__.__name__, 'status_code': 'EEE'}
        self.logger = logging.getLogger("depot")
        self.service_configs = service_configs
        self.log_request = True
        self.log_response = True
        self.raw_response_log = True
        self.log_length = 0   # can be used to reduce the length of response logs
        self.get_zip = False
        self.request_message = {}
        self.extra_log = {}
        self.api_version = None
        self.is_proto_compatible = False
        self.proto_request_class = None
        self.proto_response_class = None
        self.use_post_key = 'json'
        # Set DEFAULT_TIMEOUT in service config, otherwise default of 5 mins will be taken
        self.timeout = service_configs.DEFAULT_TIMEOUT

    def set_environment(self, action_id, api_version=None):
        """Set the request environment.

        This function is used to set the environment to make request for specific service.

        Args:
            action_id:
            api_version:

        Attributes:
            service_host:
            action_path:
            http_method:
            proxy:
            proxy_port:
            proxies:

        """
        api_host_data = self.service_configs.API_HOST[self.api_type]
        self.service_host = api_host_data['host']
        self._create_class_session(api_host=self.service_host)
        action_map = self.service_configs.API_ACTION_MAP[action_id]
        if api_version:
            action_map = action_map.get(api_version, action_map)
        default_timeout = getattr(self.service_configs, 'DEFAULT_TIMEOUT', self.timeout)
        self.timeout = action_map.get('timeout', default_timeout)
        self.action_path = action_map['path']
        self.http_method = action_map.get('method', 'GET')
        if 'proxy' in api_host_data and api_host_data.get('proxy'):
            self.proxy = api_host_data['proxy'].split(':')[0]
            self.proxy_port = api_host_data['proxy'].split(':')[-1]
            self.proxies = {
                'http': '{}:{}'.format(self.proxy, self.proxy_port),
                'https': '{}:{}'.format(self.proxy, self.proxy_port)
            }

        self.request_url = '{0}{1}'.format(
            self.service_host,
            self.action_path
        )

    @classmethod
    def _create_class_session(cls, api_host=None):
        """Create class session."""
        if cls._session is None:
            api_host = '' if api_host is None else api_host
            host_ssl = "https://%s" % api_host
            host_plain = "http://%s" % api_host
            base_session = requests.Session()
            adapter_obj = HTTPAdapter(
                pool_connections=service_configs.SERVICE_CONNECTIONS['NO_OF_POOLS'],
                pool_maxsize=service_configs.SERVICE_CONNECTIONS['POOL_MAX_SIZE']
            )
            base_session.mount(host_ssl, adapter_obj)
            base_session.mount(host_plain, adapter_obj)
            cls._session = base_session

    def create_request_headers(self, json_dict=None):
        """Create request headers with request params."""
        pass

    def create_request_message(self, msg=None):
        """Create request message with get or post params."""
        if msg and self.is_proto_compatible and self.proto_request_class:
            msg = self.create_proto_request_message(msg)

        return msg

    def create_proto_request_message(self, msg):
        """Create proto serialised request message."""
        try:
            # create an object from proto_reqeust_class.
            proto_obj = self.proto_request_class()  # pylint: disable=not-callable
            # Populate the proto object from the dict
            dict_to_protobuf(msg, proto_obj)
            # Serialize proto.
            proto_serialised_str = proto_obj.SerializeToString()
        except Exception as ex:
            self.logger.exception("%s\t%s\t%s", "proto_request_message",
                                  msg, ex, extra=self.extra_log)
            raise Exception(ex)
        return proto_serialised_str

    @classmethod
    def _make_http_call(cls, http_method, request_url, **url_params):
        """Make requests call with session."""
        resp_data = cls._session.request(http_method, request_url, **url_params)
        return resp_data

    def send_request(self, request_data=None, verify=True, files=None):     # noqa: C901
        """Send request to the request_url.

        Args:
            request_data:
            verify:
            files:

        Returns:

        """
        resp = {}
        headers = self.create_request_headers()
        if self.log_request:
            self.logger.info("%s\t%s\t%s", "request", self.request_url,
                             self.request_message, extra=self.extra_log)
        try:
            url_params = dict(
                headers=headers,
                verify=verify,
                proxies=self.proxies,
                timeout=self.timeout
            )
            if files:
                url_params['files'] = files
            if self.http_method == 'POST':
                if (self.is_proto_compatible and self.proto_request_class) or \
                        self.use_post_key == 'data':
                    url_params['data'] = request_data
                else:
                    url_params['json'] = request_data

            elif self.http_method == 'GET':
                if request_data:
                    req_data = urllib_parse.urlencode(request_data)
                    self.request_url = '{}?{}'.format(self.request_url, req_data)

            resp_data = self._make_http_call(self.http_method, self.request_url, **url_params)

            if self.raw_response_log and isinstance(resp_data, requests.models.Response):
                log_data = resp_data.content[:self.log_length] if self.log_length else \
                    resp_data.content
                self.logger.info("%s\t%s\t%s", "raw response ", resp_data.url,
                                 log_data, extra=self.extra_log)

            # step 3:
            resp = self.parse_api_response(resp_data)

        except requests.exceptions.Timeout:
            self.logger.exception("service_base.api _make_request timeout exception",
                                  extra=self.extra_log)

        except Exception as ex:
            self.logger.exception("%s\t%s\t%s", self.__class__, "_make_request", ex,
                                  extra=self.extra_log)

        if self.log_response:
            resp_log = smartjson.dumps(resp)
            # resp_log = resp.encode('ascii', 'ignore')
            self.logger.info("%s\t%s\t%s", "response ", self.request_url,
                             resp_log[:self.log_length], extra=self.extra_log)

        return resp

    def parse_api_response(self, response):
        """Parse raw response.

        Args:
            response:

        Returns:

        """
        # self.resp = copy.deepcopy(self.resp)
        resp_json = {}
        if isinstance(response, requests.models.Response):
            self.resp['status_code'] = response.status_code
        try:
            if self.get_zip:
                pass
                # dont know where to put it. for future uses
                # response = gzip.GzipFile(fileobj=io.StringIO(response)).read()
        except Exception as ex:
            self.logger.debug("%s\t%s", "parse_api_response", ex, extra=self.extra_log)

        if not response:
            self.logger.info("%s\t%s\t%s", "API no response for", self.request_url,
                             self.request_message, extra=self.extra_log)

        if response and self.is_proto_compatible and self.proto_response_class:
            resp_json = self.parse_proto_response(response)
        elif response is not None:
            resp_json = response.json()

        return resp_json

    def parse_proto_response(self, response):
        """Parse proto response."""
        resp_json = {}
        try:
            if self.proto_response_class:
                resp_proto = self.proto_response_class()    # pylint: disable=not-callable

                # Deserialize proto
                resp_proto.ParseFromString(response.content)

                # get a dict out
                resp_json = protobuf_to_dict(resp_proto)

        except Exception as ex:
            self.logger.exception("%s\t%s\t%s\t%s", "API proto response error", self.request_url,
                                  self.request_message, ex, extra=self.extra_log)
            raise Exception(ex)

        return resp_json

    def get_response(self, verify=True, **kwargs):
        """Get response.

        Returns:

        """
        self.set_environment(self.action_id, api_version=self.api_version)
        request_data = self.create_request_message()
        resp = self.send_request(request_data=request_data, verify=verify, **kwargs)

        return resp

    @staticmethod
    def get_url_params(url):
        """Get url params - path, host and query_dict.

        Args:
            url:

        Returns: (dict)

        """
        url_obj = urllib_parse.urlparse(url)
        url_params = {
            'path': url_obj.path,
            'host': url_obj.netloc
        }
        query_string_dict = urllib_parse.parse_qs(url_obj.query)
        query_dict = {k: query_string_dict[k][0] for k in query_string_dict}
        url_params['query_dict'] = query_dict
        return url_params

    @staticmethod
    def _create_content_hash(params):
        """Create request content hash.

        This function creates a hash after getting a string representation of values ordered
         on sorted keys. If value is a list do the same for the value.

        Args:
            params:

        Returns:

        """
        ord_params = OrderedDict(sorted(params.items()))
        hash_string = "|".join([str(ord_params[item]) for item in ord_params if ord_params[item]])
        hash_msg = hashlib.md5(hash_string.encode('utf-8')).hexdigest()
        return hash_msg

    @staticmethod
    def _create_hmac_signature(params, vendor_private_key):
        """Create hmac signature.

        Args:
            params:
            vendor_private_key:

        Returns:

        """
        hash_digest = ""
        if vendor_private_key:
            temp_dict = OrderedDict(sorted(params.items()))
            hash_item_list = [str(temp_dict[item]) for item in temp_dict if temp_dict[item]]
            hash_string = "|".join(hash_item_list).encode('utf-8')
            hashed_string = hmac.new(vendor_private_key, hash_string, hashlib.sha1)
            hash_digest = hashed_string.hexdigest().rstrip('\n')
        return hash_digest
