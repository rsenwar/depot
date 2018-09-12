"""GoCashV2 Api."""

import calendar
import copy
import logging
import time
from apps.app_helpers import utility

from apps.services.gocashv2 import service_configs
from apps.services.service_base import ServiceBase
from lib import smartjson


class GoCashApi(ServiceBase):
    """GoCash APIs.

    These apis interact with gocash.goibibo.com

    """

    _session = None

    def __init__(self, action_id, opts=None):
        """Initialize class GoCashApi."""
        super().__init__(action_id, opts=opts)
        self.logger = logging.getLogger(__name__)
        self.service_configs = service_configs
        self.url_params = {}
        self.extra_log = {'bucket': 'GOCASHV2', 'track_id': self.track_id, 'stage': 'API-CALL'}

    def set_environment(self, action_id, api_version=None):
        """Set the environment for request to gocash.goibibo.com.

        Attributes:
            url_params
            request_url

        """
        super().set_environment(action_id, api_version=api_version)
        request_url_format = ''
        if action_id in {'get_transaction', 'get_gocash_transaction'}:
            request_url_format = '{}{txn_id}/'
        elif action_id == 'get_balance':
            request_url_format = '{}{user_email}/'
        elif action_id == 'get_summary':
            request_url_format = '{}{user_email}/'
        elif action_id == 'user_sku_limit':
            request_url_format = '{}{user_email}/{vertical}/{parent_sku}/{child_sku}/'
        elif action_id == 'sku_limit':
            request_url_format = '{}{vertical}/{parent_sku}/{child_sku}/'
        elif action_id in {'credit', 'debit', 'revert', 'refund', 'initiate_debit',
                           'complete_debit', 'initiate_credit', 'complete_credit',
                           'complete_wallet_credit', 'cancel', 'get_credits',
                           'bulk_payment_details'}:
            request_url_format = '{}'

        if request_url_format:
            self.request_url = request_url_format.format(self.request_url, **self.options)

        self.url_params = self.get_url_params(self.request_url)

    def create_request_message(self, msg=None):
        """Create request message with get or post params."""
        msg = None
        if self.action_id in {'get_summary', }:
            key_to_add = ['limit', 'offset']
            msg = {kw: self.options[kw] for kw in key_to_add if kw in self.options}
        elif self.action_id in {'user_sku_limit', 'sku_limit'}:
            msg = {'flavour': self.options['flavour']}
        elif self.action_id in {'credit', 'debit', 'revert', 'refund', 'initiate_debit',
                                'complete_debit', 'initiate_credit', 'complete_credit',
                                'complete_wallet_credit', 'cancel', 'bulk_payment_details'}:
            msg = copy.deepcopy(self.options)
        elif self.action_id == 'get_credits':
            keys_to_add = ['user_email', 'client', 'travelamount', 'parent_sku', 'child_sku',
                           'offer_key']
            msg = {kw: self.options[kw] for kw in keys_to_add if kw in self.options}
            if 'balance_dict' in self.options:
                msg.update(self.options['balance_dict'])

        self.request_message = msg
        return msg

    def _prepare_payload(self, json_dict=None):
        """Prepare payload for request.

        Args:
            json_dict:

        Returns:

        """
        payload_dict = {}
        query_dict_params = self.url_params.get('query_dict', {})
        if query_dict_params:
            payload_dict = query_dict_params.copy()
        if json_dict:
            payload_json = smartjson.dumps(json_dict)
            payload_dict['json_payload'] = payload_json

        return payload_dict

    def _create_signature_params(self, data):
        """Create parameters for vendor's signature.

        Args:
            data:

        Returns:

        """
        request_path = self.url_params['path']
        content_md5 = self._create_content_hash(data)
        timestamp = calendar.timegm(time.gmtime())

        sign_params = {
            'content_md5': content_md5,
            'request_path': request_path,
            'request_method': self.http_method,
            'timestamp': timestamp,
        }
        return sign_params

    def _create_authorization_header(self, data):
        """Create header to be sent along data with request.

        Args:
            data:

        Returns:
            (dict)

        """
        public_key = service_configs.GOCASH_VENDOR_KEY['publicKey']
        private_key = service_configs.GOCASH_VENDOR_KEY['privateKey']
        hmac_signature = self._create_hmac_signature(data, private_key)
        authorization_key = "{}:{}".format(public_key, hmac_signature)
        headers = {
            'Date': str(data['timestamp']),
            'Authorization': authorization_key,
            'Content-MD5': data['content_md5']
        }
        return headers

    def create_request_headers(self, json_dict=None):
        """Create header for request.

        Args:
            json_dict:

        Returns:

        """
        payload_dict = self._prepare_payload(json_dict=json_dict)
        sign_params = self._create_signature_params(data=payload_dict)
        headers = self._create_authorization_header(sign_params)
        return headers

    def parse_api_response(self, response):
        """Parse raw response to given format.

        Args:
            response:

        Returns:
            (dict)

        """
        resp = super().parse_api_response(response)
        if not isinstance(resp, dict):
            resp = utility.convert_json_into_dict(resp)
        if isinstance(resp, dict) and (resp.get('success') or resp.get('error') is False):
            self.resp['success'] = True
        try:
            self.resp['message'] = self.parse_error_message(resp)
            if self.action_id in {'get_transaction', 'get_gocash_transaction',
                                  'bulk_payment_details'}:
                self.resp['data'] = resp.get('txn_list', [])
            elif self.action_id in {'get_summary', 'sku_limit', 'user_sku_limit'}:
                if 'success' not in resp:
                    self.resp['success'] = True
                    self.resp['data'] = resp
                else:
                    self.resp['data'] = {}
            elif self.action_id in {'credit', 'debit', 'revert', 'refund', 'initiate_debit',
                                    'complete_debit', 'initiate_credit', 'complete_credit',
                                    'complete_wallet_credit', 'cancel', 'get_balance'}:
                self.resp['data'] = resp.get('data', {})
            elif self.action_id == 'get_credits':
                self.resp['data'] = self.get_credits_response(response)

        except Exception as ex:
            self.logger.debug("%s\t%s", "parse_api_response", ex, extra=self.extra_log)

        return self.resp

    def parse_error_message(self, resp):
        """Parse error message to send with response.

        Args:
            resp:

        Returns:

        """
        error, opt_msg, err_msg = '', '', ''
        message = resp.get('message', '')
        if 'error' in resp:
            error = resp.get('error', '')
        if self.action_id in {'credit', 'debit', 'refund', 'revert', 'initiate_debit',
                              'complete_debit', 'initiate_credit', 'complete_credit', 'cancel',
                              'get_credits'}:
            if resp.get('error', None) is False:
                self.resp['success'] = True
            if 'errmsg' in resp:
                err_msg = resp['errmsg']
            if 'optional_msg' in resp:
                opt_msg = resp['optional_msg']

            message = "%s %s. %s" % (message, err_msg, opt_msg)
        else:
            message = "%s %s" % (message, error)
        return message.strip()

    def get_credits_response(self, response):
        """Modify the get_credits_response."""
        resp_data = {}

        distribution = response.get('optional_msg', {}).get('distribution', {})
        resp_data["vested_gocash"] = int(distribution.get('p_amt', 0))
        resp_data["bucket_gocash"] = int(distribution.get('b_amt', 0))
        resp_data["non_vested_gocash"] = \
            int(distribution.get('np_amt', 0)) + int(distribution.get('b_amt', 0))
        resp_data["non_vested_gocash_org"] = int(distribution.get('np_amt', 0))
        resp_data["max_gocash"] = int(distribution.get('t_amt', 0))
        resp_data["limit_exceeded"] = distribution.get('limit_exceeded')
        resp_data["message"] = distribution.get('message', '')

        balance = response.get('optional_msg', {}).get('balance', {})
        resp_data["vested_credits"] = int(balance.get('p_amt', 0))
        resp_data["bucket_credits"] = int(balance.get('b_amt', 0))
        resp_data["non_vested_credits"] = \
            int(balance.get('np_amt', 0)) + int(balance.get('b_amt', 0))
        resp_data["non_vested_credits_org"] = int(balance.get('np_amt', 0))
        resp_data["total_credits"] = balance.get('t_amt', 0)
        resp_data["lock"] = balance.get('is_locked', False)
        resp_data["otp"] = balance.get('OTP', False)
        resp_data["mobile"] = balance.get('Mobile', '')
        resp_data["email"] = balance.get('Email', '')
        resp_data["partial"] = True

        resp_data['sku_details'] = response.get('optional_msg', {}).get('sku_details', {})
        gc_breakup = [
            {"key": "Booking amount", "value": float(self.options.get('travelamount', 0))},
            {"key": "(Promo)goCash", "value": int(distribution.get('p_amt', 0)),
             "key_info": distribution.get('message', '')},
            {"key": "Non-Promotional",
             "value": int(distribution.get('np_amt', 0)) + int(distribution.get('b_amt', 0))},
            {"key": "Total goCash", "value": int(distribution.get('t_amt', 0))}
        ]
        resp_data['gocash_breakup'] = gc_breakup

        return resp_data


def get_api_main():
    """Get gocash Api.

    Returns:

    """
    qry = {'txn_id': 'GOHTCDV2PBK9T7C'}
    gc1 = GoCashApi('get_transaction', opts=qry)
    txn_resp = gc1.get_response()
    print("TRANCACTION::::", txn_resp)
    gc2 = GoCashApi('get_balance', opts={'user_email': 'ujjwal.tak@go-mmt.com'})
    resp = gc2.get_response()
    print('RESP ::::', resp)


if __name__ == '__main__':
    print("GOCASH API", get_api_main())
