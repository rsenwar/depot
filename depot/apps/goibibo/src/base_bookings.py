"""Base BookingDetail Module."""
from lib import smartjson
from apps.app_constants import bus_constants

__all__ = ['BaseBusBooking', ]


class BaseBusBooking(object):
    """Base Bus Booking class."""

    def __init__(self):
        """Initialize class BaseBusBooking."""

        self.status = None

        self.payment_id = self.pobj.paymentid,
        self.pnr = None
        self.db_primary_id = ''
        self.booking_refrence = None
        self.user_id = ''
        self.travell_start_date_time = ''
        self.travell_stop_date_time = None
        self.ticket_booked_date_time = ''
        self.source_city_name = None
        self.destination_city_name = None
        self.source_city_voyager_id = None
        self.destination_city_voyager_id = None
        self.travell_duration = None
        self.bus_type = None
        self.mobile_ticket = ''
        self.tracking_enabled = ''
        self.boarding_point_name = None
        self.departure_point_name = None
        self.boarding_point_time = None
        self.arrival_point_name = None
        self.cancellation_policy_url = None
        self.privacy_flag = 0
        self.traveller_name = ''
        self.ugcId = ''
        self.is_ticket_refundable = 1,
        self.is_ticket_cancellable = 1,
        self.ticket_type = '',
        self.email_id = None
        self.mobile = None
        self.booking_id = None
        self.print_pdf_url = None
        self.bus_operator_name = ''
        self.amenities = None
        self.boarding_point_contact_number = ''
        self.seat_selected = [],
        self.traveller_details = None
        self.refund_summary = None
        self.refund_summary_breakup = None
        self.amount_paid_summary = None
        self.amount_paid_breakup = None
        self.amount_paid = None
        self.business_flag = 0




