"""Bus Constants."""
from django.conf import settings

NORMAL_BOOKINGID_PREFIX = 'BUS'
BUS_ENV_TYPE = getattr(settings, 'ENVIRONMENT_NAME', 'prod')
# FLAVOURS
MOBILE_FLAVOURS = ['android', 'ios', 'winph']
BOOKING_CONFIRM_STATUS = 'to deliver'
PRE_CANCELLATION_STATUS = {'new', 'reserved', 'reserved_paylater', 'manual',
                           'to deliver'}
BOOK_SUCCESS_STATUS = {'to deliver', 'cancelled', 'to refund', 'refundqueued',
                       'refunded'}
REFUND_QUEUE_STATUS = {'to refund', 'refundqueued'}
PUSH_TO_KAFKA_STATUSES = {"to deliver", "to cancel", "to refund", "cancelled", "refundqueued",
                          "refunded", "noshow"}
