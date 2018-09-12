"""GoCashV2 Main Function API."""

import logging

from apps.services.gocashv2 import service_configs
from apps.services.gocashv2.api import GoCashApi
from lib import smartjson

logger = logging.getLogger(__name__)


class GoCashV2(object):
    """GoCashV2 Module Functions.

    This Class interacts with GoCashV2 APIs and returns formatted response.

    """

    # pylint: disable=too-many-public-methods
    @staticmethod
    def get_transaction(txn_id):
        """Get gocash transaction list.

        Args:
            txn_id:

        Returns:

        """
        resp = {'success': False, 'message': ''}
        if not txn_id:
            resp['message'] = service_configs.GOCASH_MESSAGES['GC400']
        else:
            try:
                opts = {'txn_id': txn_id}
                if txn_id[:6].upper() == 'GOCRED':
                    action_id = "get_gocash_transaction"
                else:
                    action_id = 'get_transaction'
                gocash_api_obj = GoCashApi(action_id, opts=opts)
                resp = gocash_api_obj.get_response()
            except Exception as ex:
                logger.exception("%s\t%s\t%s", "Gocashv2.main get_transaction", txn_id, ex)

        return resp

    @staticmethod
    def get_transaction_gc(txn_id, txn_type='booking', txn_state='success'):
        """Get the gocash txn details.

        This function return gocash txn details that are associated with the
        payment-transaction-id.

        Args:
            txn_id:
            txn_type :(string) "booking"/"refund"/"promo"
            txn_state:

        Returns:

        """
        resp = {'success': False, 'message': ''}
        txn_list, promo, bucket, non_promo, total = [], 0, 0, 0, 0
        gc_txn_id = ''
        if txn_id[:6].upper() == 'GOCRED':
            gc_txn_id = txn_id
        resp = GoCashV2.get_transaction(txn_id)
        txn_list = resp.get('data', [])
        if txn_list:
            if gc_txn_id == '':
                txn_list_filter = filter(
                    lambda x: x.get('txn_type') == txn_type and x.get("txn_state") == txn_state,
                    txn_list)
                txn_list = list(txn_list_filter)
            if not txn_list:
                resp['message'] = service_configs.GOCASH_MESSAGES['GC404']

        try:
            for txn in txn_list:
                promo += txn.get('promo_txn_amt', 0)
                bucket += txn.get('bucket_txn_amt', 0)
                non_promo += txn.get('non_promo_txn_amt', 0)
                total += txn.get('total_txn_amount', 0)
                gc_txn_id = txn.get('gocash_txn_id', '')
        except Exception as ex:
            logger.exception("%s\t%s\t%s", "Gocashv2.main get_transaction_gc", txn_id, ex)

        resp['data'] = {
            'promo': int(promo),
            'bucket': int(bucket),
            'non_promo': int(non_promo),
            'total': int(total),
            'gc_txn_id': gc_txn_id
        }

        if gc_txn_id:
            resp['success'] = True

        return resp

    @staticmethod
    def get_applied_gocash(paymentid):
        """Return applied gocash in a transaction.

        Args:
            paymentid:

        Returns:

        """
        applied_gocash = {'npgc': 0, 'pgc': 0, 'b_npgc': 0, 'r_npgc': 0, 'tgc': 0}
        if paymentid:
            transaction = GoCashV2.get_transaction_gc(paymentid)
            if transaction.get('total'):
                applied_gocash['tgc'] = transaction.get('total', 0)
                applied_gocash['pgc'] = transaction.get('promo', 0)
                applied_gocash['npgc'] = transaction.get('non_promo', 0) \
                    + transaction.get('bucket', 0)
                applied_gocash['b_npgc'] = transaction.get('bucket', 0)
                applied_gocash['r_npgc'] = transaction.get('non_promo', 0)

        return applied_gocash

    @staticmethod
    def get_refunded_gocash(paymentid):
        """Return refunded gocash with a paymentid.

        Args:
            paymentid:

        Returns:

        """
        refund_gocash = {'npgc': 0, 'pgc': 0, 'b_npgc': 0, 'r_npgc': 0, 'tgc': 0}
        if paymentid:
            transaction = GoCashV2.get_transaction_gc(paymentid, txn_type='refund')
            if transaction.get('total'):
                refund_gocash['tgc'] = transaction.get('total', 0)
                refund_gocash['pgc'] = transaction.get('promo', 0)
                refund_gocash['npgc'] = transaction.get('non_promo', 0) \
                    + transaction.get('bucket', 0)
                refund_gocash['b_npgc'] = transaction.get('bucket', 0)
                refund_gocash['r_npgc'] = transaction.get('non_promo', 0)

            transaction = GoCashV2.get_transaction_gc(paymentid, txn_type='record-refund-expire')
            if transaction.get('total'):
                refund_gocash['tgc'] += transaction.get('total', 0)
                refund_gocash['pgc'] += transaction.get('promo', 0)
                refund_gocash['npgc'] += transaction.get('non_promo', 0) \
                    + transaction.get('bucket', 0)
                refund_gocash['b_npgc'] += transaction.get('bucket', 0)
                refund_gocash['r_npgc'] += transaction.get('non_promo', 0)

        return refund_gocash

    @staticmethod
    def get_actual_gocash_paid(gocash_txn, gocash_refund):
        """Return actual gocash used in transaction.

         This function returns actual gocash paid by the customer in case of a
          transaction with refund gocash.

        Args:
            gocash_txn:
            gocash_refund:

        Returns:

        """
        gocash_txn['tgc'] = gocash_txn['tgc'] - gocash_refund.get('tgc', 0)
        gocash_txn['pgc'] = gocash_txn['pgc'] - gocash_refund.get('pgc', 0)
        gocash_txn['npgc'] = gocash_txn['npgc'] - gocash_refund.get('npgc', 0)
        gocash_txn['b_npgc'] = gocash_txn['b_npgc'] - gocash_refund.get('b_npgc', 0)
        gocash_txn['r_npgc'] = gocash_txn['r_npgc'] - gocash_refund.get('r_npgc', 0)

        return gocash_txn

    @staticmethod
    def get_balance(user_email):
        """Get user gocash balance.

        Args:
            user_email:

        Returns: (dict) ..
        resp['data]
            credits_id: (int)
            t_amt: (int)
            p_amt: (int)
            b_amt: (float)
            np_amt: (int)

        """
        resp = {'success': False, 'message': ''}
        try:
            if not user_email:
                resp['message'] = service_configs.GOCASH_MESSAGES['GCB403']
            else:
                opts = {'user_email': user_email}
                action_id = 'get_balance'
                gc_api_obj = GoCashApi(action_id, opts=opts)
                resp = gc_api_obj.get_response()
        except Exception as ex:
            logger.exception("%s\t%s\t%s\t%s", "services GoCashV2", "Exception in get_balance ",
                             user_email, ex)

        return resp

    @staticmethod
    def get_summary(user_email, limit='30', offset='0'):
        """Return summary for a user email.

        Args:
            user_email:
            limit:
            offset:

        Returns: (dict)
        resp['data']
            count: (int)
            results: (list) [Gocash transactions]
            balance: (dict) [GoCash]


        """
        resp = {'success': False, 'message': ''}
        try:
            if not user_email:
                resp['message'] = service_configs.GOCASH_MESSAGES['GCB403']
            else:
                opts = {'user_email': user_email, 'limit': limit, 'offset': offset}
                action_id = 'get_summary'
                gc_api_obj = GoCashApi(action_id, opts=opts)
                resp = gc_api_obj.get_response()
        except Exception as ex:
            logger.exception("%s\t%s\t%s\t%s", "services GoCashV2", "Exception in get_summary ",
                             user_email, ex)

        return resp

    @staticmethod
    def get_sku_limit(flavour, vertical, sku_params=None, user_email=None):
        """Return credits limit for specific sku.

        Args:
            flavour:
            vertical:
            sku_params:
                parent_sku:
                child_sku:
            user_email:

        Returns:
            resp['data']:
                sku:
                parent_sku:
                default:
                    sku: (string)
                    container_id: (String) '#' separated.
                    gravity: (int)
                    duration: (int)
                    velocity: (int)
                    percentage: (int)
                    _id: (String)

        """
        resp = {'success': False, 'message': ''}
        if sku_params is None:
            sku_params = {}
        try:
            if not flavour or not vertical:
                resp['message'] = service_configs.GOCASH_MESSAGES['GCB405']
            else:
                if user_email:
                    action_id = 'user_sku_limit'
                else:
                    action_id = 'sku_limit'
                parent_sku = sku_params.get('parent_sku', 'default')
                opts = {
                    'vertical': vertical,
                    'flavour': flavour,
                    'parent_sku': sku_params.get('parent_sku', 'default'),
                    'child_sku': sku_params.get('child_sku', parent_sku)
                }
                if user_email:
                    opts['user_email'] = user_email

                gc_api_obj = GoCashApi(action_id, opts=opts)
                resp = gc_api_obj.get_response()
        except Exception as ex:
            logger.exception("%s\t%s\t%s\t%s\t%s", " Exception get_sku_limit",
                             flavour, vertical, sku_params, ex)

        return resp

    @staticmethod
    def credit_gocash(data):
        """Credit gocash in one shot.

        Args:
            data: (dict)
                'vertical': 'hotels',
                'txn_id': 'xyz',
                'user_email': 'abc@abc.com',
                'type': 'promo', (bucket/cashback/refund/load_wallet/load_Wallet_bonus)
                'non_promotional_amount': int(value),
                'promotional_amount': 0,
                'bucket_amount': 0,
                'set_auto_expiry_date': True
            }

        Returns:(dict)
            resp['data']
                'balance':
                    'start': (dict)
                    'end': (dict)
                'transaction': (dict)
                'wallet_info': (dict)

        """
        response = {}
        try:
            action_id = 'credit'
            gc_api_obj = GoCashApi(action_id, opts=data)
            response = gc_api_obj.get_response()
        except Exception as ex:
            logger.exception("%s\t%s\t%s", " Exception credit_gocash", data, ex)

        return response

    @staticmethod
    def debit_gocash(data):
        """Debit gocash in one shot.

        Args:
            data: {
                "user_id": user_id,
                "vertical": 'hotels',
                "txn_id": paymentid,
                "type": 'booking',
                "promotional_amount": (int) Value,
                "non_promotional_amount": (int) value,
                "bucket_amount": (int) Value,
                "parent_sku": 'parent_sku',
                "child_sku": 'child_sku',
                "flavour": 'flavour',
                "user_email": user_email,
            }


        Returns:

        """
        response = {}
        try:
            action_id = 'debit'
            if (data.get('parent_sku') or data.get('child_sku')) and not data.get('skus'):
                data['skus'] = {
                    'parent_sku': data.get('parent_sku', 'default'),
                    'child_sku': data.get('child_sku', 'default')
                }
            gc_api_obj = GoCashApi(action_id, opts=data)
            response = gc_api_obj.get_response()
        except Exception as ex:
            logger.exception("%s\t%s\t%s", " Exception credit_gocash", data, ex)

        return response

    @staticmethod
    def refund_gocash(data):
        """Refund gocash in one shot.

        Args:
            data:

        Returns:

        """
        response = {}
        try:
            action_id = 'refund'
            gc_api_obj = GoCashApi(action_id, opts=data)
            response = gc_api_obj.get_response()
        except Exception as ex:
            logger.exception("%s\t%s\t%s", " Exception refund_gocash", data, ex)

        return response

    @staticmethod
    def revert_gocash(data):
        """Revert gocash in one shot.

        Args:
            data:

        Returns:

        """
        response = {}
        try:
            action_id = 'revert'
            gc_api_obj = GoCashApi(action_id, opts=data)
            response = gc_api_obj.get_response()
        except Exception as ex:
            logger.exception("%s\t%s\t%s", " Exception revert_gocash", data, ex)

        return response

    @staticmethod
    def cancel_gocash_transaction(data):
        """Cancel the gocash transation.

        Args:
            data:

        Returns:

        """
        resp = {}
        try:
            action_id = 'cancel'
            if not data.get('gocash_txn_id'):
                resp['message'] = service_configs.GOCASH_MESSAGES['GC400']
            else:
                gc_api_obj = GoCashApi(action_id, opts=data)
                resp = gc_api_obj.get_response()
        except Exception as ex:
            logger.exception("%s\t%s\t%s", " Exception revert_gocash", data, ex)

        return resp

    @staticmethod
    def initiate_gocash_debit(data):
        """Initialize gocash debit in two shot debit process.

        Gocash debit is not complete until you call ``complete_gocash_debit``.

        Args:
            data:

        Returns:

        """
        response = {}
        try:
            action_id = 'initiate_debit'
            if not data.get('sku_list'):
                sku_list = [[data.get('parent_sku', 'default'), data.get('child_sku', 'default')]]
                data['sku_list'] = sku_list
            gc_api_obj = GoCashApi(action_id, opts=data)
            response = gc_api_obj.get_response()
        except Exception as ex:
            logger.exception("%s\t%s\t%s", " Exception initiate_gocash_debit", data, ex)

        return response

    @staticmethod
    def complete_gocash_debit(data):
        """Complete gocash debit in two-shot debit process.

        Gocash debit is to be initiated with API call 'initiate_gocash_debit'

        Args:
            data:

        Returns:

        """
        response = {}
        try:
            action_id = 'complete_debit'
            if not data.get('sku_list'):
                sku_list = [[data.get('parent_sku', 'default'), data.get('child_sku', 'default')]]
                data['sku_list'] = sku_list
            gc_api_obj = GoCashApi(action_id, opts=data)
            response = gc_api_obj.get_response()
        except Exception as ex:
            logger.exception("%s\t%s\t%s", " Exception complete_gocash_debit", data, ex)

        return response

    @staticmethod
    def initiate_gocash_credit(data):
        """Initialize gocash credit in two-shot process.

        Args:
            data:

        Returns:

        """
        response = {}
        try:
            action_id = 'initiate_credit'
            gc_api_obj = GoCashApi(action_id, opts=data)
            response = gc_api_obj.get_response()
        except Exception as ex:
            logger.exception("%s\t%s\t%s", " Exception initiate_gocash_credit", data, ex)

        return response

    @staticmethod
    def complete_gocash_credit(data):
        """Complete gocash credit in two-shot process.

        Args:
            data:

        Returns:

        """
        response = {}
        try:
            action_id = 'complete_credit'
            gc_api_obj = GoCashApi(action_id, opts=data)
            response = gc_api_obj.get_response()
        except Exception as ex:
            logger.exception("%s\t%s\t%s", " Exception complete_gocash_credit", data, ex)

        return response

    @staticmethod
    def complete_wallet_credit(status, gocash_txn_id):
        """Complete wallet credit which initiated earlier.

        Args:
            status:
            gocash_txn_id:

        Returns:

        """
        response = {}
        try:
            action_id = 'complete_wallet_credit'
            opts = {
                'status': status,
                'gocash_txn_id': gocash_txn_id
            }
            gc_api_obj = GoCashApi(action_id, opts=opts)
            response = gc_api_obj.get_response()
        except Exception as ex:
            logger.exception("%s\t%s\t%s\t%s", " Exception complete_gocash_credit", status,
                             gocash_txn_id, ex)

        return response

    @staticmethod
    def get_credits(user_email, flavour, vertical, travel_amount=0, parent_sku='default',
                    child_sku='default', **kwargs):
        """Return applicable credits and gocash raw response.

        This api returns balance and distribution on specific travelamount, gocash balance,
        sku details.

        Args:
            user_email:
            flavour:
            vertical:
            travel_amount:
            parent_sku:
            child_sku:
            kwargs:
                offer_key:
                balance_dict:

        Returns:

        """
        # pylint: disable=too-many-arguments
        resp = {}
        opts = {}
        try:
            if not user_email:
                resp['message'] = service_configs.GOCASH_MESSAGES['GC400']
            elif not vertical or not flavour:
                resp['message'] = service_configs.GOCASH_MESSAGES['GCB405']
            else:
                action_id = 'get_credits'
                opts = {
                    'user_email': user_email,
                    'client': vertical,
                    'travelamount': str(travel_amount),
                    'parent_sku': parent_sku,
                    'child_sku': child_sku,
                    'flavour': flavour
                }
                if kwargs.get('offer_key'):
                    opts['offer_key'] = kwargs['offer_key']
                if kwargs.get('balance_dict'):
                    opts['balance_dict'] = kwargs['balance_dict']

                gc_api_obj = GoCashApi(action_id, opts=opts)
                response = gc_api_obj.get_response()
                resp = response['data']
        except Exception as ex:
            logger.exception("%s\t%s\t%s", "Exception in get_credits ", opts, ex)

        return resp

    @staticmethod
    def get_applicable_gc(user_email, flavour, vertical, travel_amount=0, parent_sku='default',
                          child_sku='default', **kwargs):
        """Return balance and distribution of vested and non-vested gocash and credits.

        Args:
            user_email:
            flavour:
            vertical:
            travel_amount:
            parent_sku:
            child_eku:
            kwargs:
                offer_key:
                balance_info:

        Returns:

        """
        # pylint: disable=too-many-arguments
        resp = {}
        if not user_email:
            resp['message'] = service_configs.GOCASH_MESSAGES['GC400']
        elif not vertical or not flavour:
            resp['message'] = service_configs.GOCASH_MESSAGES['GCB405']
        else:
            try:
                # restricting bus user to use gocash+
                guidance_dict = getattr(service_configs, 'GOCASH_BUCKET_RESTRICTIONS', {})
                banned_verticals = guidance_dict.get('BANNED_VERTICALS_BURN', [])
                balance_dict = {}
                if guidance_dict and vertical in banned_verticals:
                    user_balance = GoCashV2.get_balance(user_email)
                    if user_balance['success']:
                        gc_data = user_balance.get('data', {})
                        gc_data['t_amt'] -= int(gc_data['b_amt'])
                        gc_data['b_amt'] = 0
                        for key in gc_data:
                            balance_dict[key] = gc_data[key]
                    balance_dict['passing_balance'] = True

                resp = GoCashV2.get_credits(user_email, flavour, vertical,
                                            travel_amount=travel_amount, parent_sku=parent_sku,
                                            child_sku=child_sku, balance_dict=balance_dict,
                                            **kwargs)
                if resp and guidance_dict and vertical in banned_verticals:
                    resp['go_cash_breakup'][1]['key_info'] += \
                        service_configs.GOCASH_BAN_MSG % vertical
                    resp['message'] += service_configs.GOCASH_BAN_MSG % vertical
            except Exception as ex:
                logger.exception("%s\t%s", "Exception in get_applicable_gc ", ex)

        return resp

    @staticmethod
    def get_bulk_gocash_payment_txn_detail(paymentid_list):
        """Get bulk payment txn details gocash.

        Args:
            paymentid_list:

        Returns:

        """
        txn_list = []
        try:
            action_id = 'bulk_payment_details'
            opts = {
                'payment_txnid': paymentid_list
            }
            gc_api_obj = GoCashApi(action_id, opts=opts)
            response = gc_api_obj.get_response()
            txn_list = response.get('data', [])
        except Exception as ex:
            logger.exception("%s\t%s", "Exception in get_bulk_gocash_payment_txn_detail ", ex)

        return txn_list

    @staticmethod
    def get_gocash_breakup(paymentid_list, txn_list=None, txn_type=None,
                           txn_state='success'):
        """Get gocash refund breakup.

        Args:
            paymentid_list:
            txn_list:
            txn_type:
            txn_state:

        Returns: (dict)

        """
        # pylint: disable=too-many-nested-blocks
        gc_refund = {}
        if txn_list is None:
            txn_list = GoCashV2.get_bulk_gocash_payment_txn_detail(paymentid_list)
        for txn in txn_list:
            for key, value in txn.items():
                if value.get('txn_type') == txn_type and value.get('txn_state') == txn_state:
                    try:
                        item = {}
                        gocash = int(value.get('promo_txn_amt', 0))
                        bucket_txn_amt = int(value.get('bucket_txn_amt', 0))
                        non_promo_txn_amt = int(value.get('non_promo_txn_amt', 0))

                        if bucket_txn_amt <= 0:
                            if value.get('extra_params', {}):
                                extra_params = value['extra_params']
                                if not isinstance(extra_params, dict):
                                    extra_params = smartjson.loads(extra_params)
                                bucket_txn_amt = int(extra_params.get('bucket_amount_refunded', 0))

                        item['pgc'] = gocash
                        item['npgc'] = bucket_txn_amt + non_promo_txn_amt
                        item['r_npgc'] = non_promo_txn_amt
                        item['b_npgc'] = bucket_txn_amt
                        gc_refund[key] = item
                    except Exception as ex:
                        logger.exception("%s\t%s", "Exception in get_gocash_refund_breakup ", ex)

        return gc_refund
