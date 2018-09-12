"""Service Configs for GoCashV2 API."""
from django.conf import settings

GOCASH_PUBLIC_KEY = 'GOI200KIRA'
GOCASH_PRIVATE_KEY = 'sH35$8&RVb*vSjrp4AJ6'

GOCASH_HOST = getattr(settings, 'GOCASH_HOST', 'localhost:8000')
API_HOST = {
    'prod': {'host': 'http://gocash.goibibo.com'},
    'test': {'host': 'http://gocashpp.goibibo.com'},
    'pp': {'host': 'http://gocashpp.goibibo.com'},
    'dev': {'host': 'http://' + GOCASH_HOST},
    'prodpp': {'host': 'http://newprodpp.goibibo.com'},
}

API_ACTION_MAP = {
    'get_balance': {'path': '/v1/statement/user/balance/', 'method': 'GET'},
    'get_credits': {'path': '/v1/statement/user/limits/', 'method': 'GET'},
    'get_summary': {'path': '/v1/statement/user/summary/', 'method': 'GET'},
    'sku_limit': {'path': '/v1/limits/sku/', 'method': 'GET'},
    'user_sku_limit': {'path': '/v1/limits/user/', 'method': 'GET'},
    'get_transaction': {'path': '/v1/statement/user/paymenttxndetail/', 'method': 'GET'},
    'get_gocash_transaction': {'path': '/v1/statement/user/gocashtxndetail/', 'method': 'GET'},
    'complete_wallet_credit': {'path': '/v1/load/complete_load_wallet/', 'method': 'GET'},

    'credit': {'path': '/v2/gocash/credit/', 'method': 'POST'},
    'debit': {'path': '/v2/gocash/debit/', 'method': 'POST'},
    'revert': {'path': '/v2/gocash/revert/', 'method': 'POST'},
    'refund': {'path': '/v2/gocash/refund/', 'method': 'POST'},
    'cancel': {'path': '/v2/gocash/cancel/', 'method': 'POST'},
    'initiate_debit': {'path': '/v2/gocash/initiate_debit/', 'method': 'POST'},
    'complete_debit': {'path': '/v2/gocash/complete_debit/', 'method': 'POST'},
    'initiate_credit': {'path': '/v2/gocash/initiate_credit/', 'method': 'POST'},
    'complete_credit': {'path': '/v2/gocash/complete_credit/', 'method': 'POST'},
    'bulk_payment_details': {'path': '/v1/statement/user/Bulkpaymenttxndetail/', 'method': 'POST'},
}

GOCASH_MESSAGES = {
    'GC400': 'Request parameters are not provided.',
    'GC404': 'No gocash transaction found.',
    'GCB403': 'User Email missing in parameters.',
    'GCB405': 'Flavour/Vertical missing in parameters.'
}

GOCASH_VENDOR_KEY = {
    'publicKey': 'goibibo',
    'privateKey': b'sH35$8&RVb*vSjrp4AJ6'
}

GOCASH_BUCKET_RESTRICTIONS = {'BANNED_VERTICALS_BURN': [], 'EARN_CAP': 500}

GOCASH_BAN_MSG = ' goCash+ earned through special promotions cannot be redeemed on %s Bookings.'
