"""ListBookings Module."""
import logging

from apps.app_constants.config_params import bus_config_params
from apps.goibibo.helpers import custom_model_helpers
from apps.goibibo.models import CancelTicket
from apps.services.gocashv2 import GoCashV2


logger = logging.getLogger(__name__)


class ListBusBooking(object):
    """Class ListHotelBooking."""

    def __init__(self):
        """Initialize class listhotelbooking."""
        self.bus_bookings = []
        self.bus_booking_id_list = set()
        self.guid_list = set()
        self.payment_id_list = set()
        self.bus_bookings_dict = {}

    def add_bus_bookings(self, queryset, filo_response=None,   # noqa: C901
                           fetch_filo=True):
        """Add all booking_obj in hotel_bookings."""
        for item in queryset:
            bb_obj = BusBooking(fetch_in_list=True, fetch_filo=fetch_filo)
            bb_obj.fetch_booking_details(item)
            self.bus_bookings.append(bb_obj)
            self.bus_bookings_dict[bb_obj.bookingid] = bb_obj
            if bb_obj.hotel_voyagerid:
                self.bus_booking_id_list.add(bb_obj.bookingid)
                self.guid_list.add(bb_obj.guid)

        combined_ref_data = self._fetch_refund_data()
        combined_users_data = self._fetch_users_with_guid()


        for hb_obj in self.hotel_bookings:
            hb_obj.assign_voyager_data(combined_voy_data)
            hb_obj.get_refund_breakup(combined_ref_data)
            hb_obj.user = combined_users_data.get(hb_obj.guid, None)
            hb_obj.user_id = 0 if hb_obj.user is None else hb_obj.user.id
            if not fetch_filo:
                self._add_filo_response(hb_obj, filo_response)
            if hb_obj.is_cart_booking:
                cart_hotel_obj = combined_cart_data.get(hb_obj.cart_bookingid)
                if cart_hotel_obj:
                    hb_obj.cart_object = cart_hotel_obj.instance
                    hb_obj.cart_hotel_object = cart_hotel_obj

    def add_hotel_bookings_f1(self, queryset):   # noqa: C901
        """Add all booking_obj in hotel_bookings."""
        for item in queryset:
            hb_obj = HotelBooking(fetch_filo=False)
            hb_obj.fetch_booking_detail_f1(item)
            self.hotel_bookings.append(hb_obj)
            self.hotel_bookings_dict[hb_obj.bookingid] = hb_obj

    @staticmethod
    def _add_filo_response(hotel_booking, filo_response):
        """Add filo response to hotel bookings."""
        filo_response = {} if filo_response is None else filo_response
        vertical = 'domhotel' if hotel_booking.is_domestic else 'inthotel'
        filo_resp = filo_response.get(vertical, {})
        if filo_resp:
            hotel_booking.assign_filo_response(filo_resp)

    def _fetch_voyager_data(self):
        """Fetch voyager data for hotel_bookings."""
        caching_voyager_flag = hotels_config_params.get('caching_voyager_data_config', 0)
        caching_voyager_flag = bool(int(caching_voyager_flag))
        voy_data = VoyagerData().get_multiple_hotels_data(
            list(self.vh_id_list), from_cache=caching_voyager_flag)
        return voy_data

    def _fetch_refund_data(self):
        """Fetch refund data for hotel_bookings."""
        cancel_data = dict()
        for bkid in self.hotel_booking_id_list:
            cancel_data[bkid] = []
        try:
            cancel_list = CancelTicket.objects\
                .filter(cancelbookingid__in=list(self.hotel_booking_id_list))
            for cancel_obj in cancel_list:
                cancel_data[cancel_obj.cancelbookingid].append(cancel_obj)
        except Exception as ex:
            logger.debug("%s\t%s", "fetch_refund_data", ex)

        return cancel_data

    def _fetch_users_with_guid(self):
        """Fetch user_ids for hotel_bookings."""
        users = custom_model_helpers.get_custom_users(list(self.guid_list))
        return users

    def _fetch_user_ids_with_guid(self):
        """Fetch user_ids for hotel_bookings."""
        user_ids = custom_model_helpers.get_custom_user_ids(list(self.guid_list))
        return user_ids

    def _fetch_cart_hotel_bookings(self):
        """Fetch cart_objects for hotel_bookings."""
        cart_data = dict()
        try:
            from apps.goibibo.src.cart_bookings import CartHotelBooking
            cart_bookings = CartBooking.objects\
                .filter(bookingid__in=list(self.cart_booking_id_list))
            for cart_obj in cart_bookings:
                chb_obj = CartHotelBooking(fetch_in_list=True)
                chb_obj.fetch_booking_details(cart_obj)
                child_bookings = []
                booking_detail_hotels = []
                for chld_bkgid in chb_obj.child_booking_ids:
                    chld_obj = self.hotel_bookings_dict.get(chld_bkgid)
                    if chld_obj is None:
                        child_bookings = chb_obj.get_child_bookings()
                        booking_detail_hotels = chb_obj.booking_detail_hotels
                        break
                    else:
                        child_bookings.append(chld_obj)
                        booking_detail_hotels.append(chld_obj.instance)
                chb_obj.child_bookings = child_bookings
                chb_obj.booking_detail_hotels = booking_detail_hotels

                cart_data[chb_obj.bookingid] = chb_obj
        except Exception as ex:
            logger.exception("%s\t%s", "fetch_cart_hotel_bookings", ex)

        return cart_data

    def _fetch_gocash_refund_breakup(self):
        """Fetch gocash refund breakup in bulk."""
        gc_refund_breakup = GoCashV2.get_gocash_breakup(list(self.payment_id_list),
                                                        txn_type='refund', txn_state='success')
        return gc_refund_breakup
