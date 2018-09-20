"""Resource for my booking data."""
import logging

import simplejson
from django.conf import settings

from apps.goibibo.models.common_models import RefundBreakup
from apps.goibibo.models.custom_user_models import CustomUserProfile, User
from apps.services.gocashv2 import GoCashV2
from lib import smart_newrelic

logger = logging.getLogger(__name__)


class MyBookings(object):
    """MyBookings class.

    It takes queryset from bus_paymentdetail and prepares data for my booking response.

    """

    @staticmethod
    def get_my_bookings_data(queryset, user_id=0):
        """Get my_bookings data for list of payment_objects."""
        for bb_obj in queryset:
            try:
                yield MyBookings.get_bus_booking_data(bb_obj, user_id)
            except Exception:
                smart_newrelic.push_transaction_exception()
                logger.exception("Exception in MyBookings.get_my_bookings_data")

    @staticmethod
    def get_bus_booking_data(queryset, user_id):
        """Get bus_booking details for a bus_booking object."""
        tax = bfare = 0
        json_result = []
        for payobj in queryset:
            #rfs, refund_breakup = MyBookings.get_rfs_rfm(payobj)
            (rfs, rfm, ypm, yps, yp) = MyBookings.get_payment_breakup(payobj)
            travellerdetails = MyBookings.get_traveller_details(payobj)
            try:
                data = {}
                #promoname = ''
                bj = simplejson.loads(payobj.bookjson)
                try:
                    if bj['DPName'] == -1:
                        bj['DPName'] = ''
                    else:
                        bj['DPName'] = str(bj['DPName'])
                except Exception:
                    bj['DPName'] = ''
                try:
                    dpname = bj.get('ConfirmTicket', {}).get('DPDetails', {}).get('DPName')
                    dptime = bj.get('ConfirmTicket', {}).get('DPDetails', {}).get('DPTime')
                except Exception:
                    dpname = ''
                    dptime = bj['arrdate'].replace('Z', '')
                try:
                    bpcn = bj.get('ConfirmTicket', {}).get('BPDetails', '').get('BPContactNumber').split(',')
                    bpt = bj.get('ConfirmTicket', {}).get('BPDetails', '').get('BPTime')
                except Exception:
                    bpcn = ''
                    bpt = ''
                pf = bj.get('privacy_flag', 'NA')
                if pf in ['false', '0', 'NA']:
                    bj['privacy_flag'] = 0
                elif pf == 'true' or pf == '1':
                    bj['privacy_flag'] = 1
                elif pf == '-1':
                    bj['privacy_flag'] = -1
                if 'fare' in bj and 'totalfare' in bj['fare']:
                    bj['fare']['totalfare'] = float(bj['fare']['totalfare'])
                for seat in bj['seatsSelected']:
                    tax += float(seat.get('stax', 0))
                    bfare += float(seat.get('bfare', 0))
                    seat['bfare'] = float(seat.get('bfare', 0))
                #tr = simplejson.loads(payobj.travellerdetails)
                #if 'promo' in bj:
                #    promoname = bj['promo'].get('promoname')
                operator_pnr = bj.get('ConfirmTicket', {}).get('TravelOperatorPNR', '')

                data['status'] = payobj.status
                data['payment_id'] = payobj.paymentid
                data['pnr'] = operator_pnr
                data['db_primary_id'] = payobj.id
                data['booking_refrence'] = operator_pnr
                data['user_id'] = str(MyBookings.get_userid(payobj.guid))
                data['travell_start_date_time'] = bj['depdate'].replace('Z', '')
                data['travell_stop_date_time'] = dptime
                data['ticket_booked_date_time'] = str(payobj.bookingdate)
                data['source_city_name'] = bj['origin']
                data['destination_city_name'] = bj['destination']
                data['source_city_voyager_id'] = bj.get('src_voyager_id', '')
                data['destination_city_voyager_id'] = bj.get('dest_voyager_id', '')
                data['travell_duration'] = bj['duration']
                data['bus_type'] = bj['BusType']
                data['mobile_ticket'] = str(bj.get('mTicket', 'False'))
                data['tracking_enabled'] = str(bj.get('gps', 'False'))
                data['boarding_point_name'] = bj.get('BPName', '').split('-')[1]
                data['departure_point_name'] = bj.get('BPName', '').split('-')[1]
                data['boarding_point_time'] = bpt
                data['arrival_point_name'] = dpname
                data['cancellation_policy_url'] = MyBookings.get_cpurl(payobj.bookingid)
                data['privacy_flag'] = bj.get('privacy_flag', 0)
                data['traveller_name'] = payobj.firstname
                data['ugcId'] = str(bj.get('ugcid', ''))
                data['is_ticket_refundable'] = 1
                data['is_ticket_cancellable'] = 1
                data['ticket_type'] = ''
                data['email_id'] = payobj.email
                data['mobile'] = payobj.mobile
                data['booking_id'] = payobj.bookingid
                data['print_pdf_url'] = MyBookings.get_ticket(payobj)
                data['bus_operator_name'] = bj.get('TravelsName', '')
                data['amenities'] = bj.get('amenities', 'NA').split(',')
                data['boarding_point_contact_number'] = bpcn
                data['seat_selected'] = [key['seat'] for key in bj.get('seatsSelected')]
                data['traveller_details'] = travellerdetails
                data['refund_summary'] = rfs
                data['refund_summary_breakup'] = rfm
                data['amount_paid_summary'] = yps
                data['amount_paid_breakup'] = ypm
                data['amount_paid'] = yp
                data['business_flag'] = 0 if bj.get('gst_data', {}).get('profile', 'personal') == 'personal' else 1
            except Exception as ex:
                logger.exception("%s\t%s", "get_bus_booking_data", ex)
                data = {}
            if data != {}:
                json_result.append(data)
        return json_result



    @staticmethod
    def get_rfs_rfm(pay_obj):
        """Get bus_booking refund map and summary.
        this function returns refundsummary as dict and refundmap as list.
        Returns: dict, List
        """
        status_map = {"to deliver": "OK",
                      "to refund": "CANCELLED",
                      "pending": "CANCELLED",
                      "refunded": "CANCELLED",
                      "charged": "OK"}
        refund_breakup = []
        rfs = {}
        gocash = gocashP = 0 # cash = credits = 0
        refund_breakupobj_map = {'cash': 0, 'credits': 0}
        if status_map.get(pay_obj.status, "OK") == 'CANCELLED':
            refund_breakupobj = RefundBreakup.objects.filter(paymentid=pay_obj.paymentid)
            #gocash_refund_breakupobj = None
            get_refunded_gocash = MyBookings.get_refunded_gocash(pay_obj.paymentid)
            #for breakupobj in gocash_refund_breakupobj:
            #    gocash += float(breakupobj.VestedAmount)
            #    gocashP += float(breakupobj.CreditsAmount) + float(breakupobj.BucketAmount)
            gocash += float(get_refunded_gocash.get('pgc', 0))
            gocashP += float(get_refunded_gocash.get('npgc', 0))
            refund_breakup.append({'k': 'credits', 'v': str(gocash), 'c': 'INR'})
            refund_breakup.append({'k': 'goCash+', 'v': str(gocashP), 'c': 'INR'})
            for breakupobj in refund_breakupobj:
                refund_breakupobj_map[breakupobj.refund_type] += float(breakupobj.refund)
                if breakupobj.refund_type == 'cash':
                    refundmap = {'k': 'refund to card', 'v': str(refund_breakupobj_map[breakupobj.refund_type]),
                                 'c': ''}
                    rfs.update(refundmap)

        return rfs, refund_breakup

    @staticmethod
    def get_refunded_gocash(payment_id):
        """Get refunded gocash with cancellation.
        this function returns gocash refunded with this booking.
        Returns: (dict)
        """
        gc_refunded = {'npgc': 0, 'pgc': 0, 'b_npgc': 0, 'r_npgc': 0, 'tgc': 0}
        gc_refunded = GoCashV2.get_refunded_gocash(payment_id)
        return gc_refunded


    @staticmethod
    def get_userid(guid):
        """Get user if from guid.
        this function returns users user id.
        Returns: (int)
        """
        user_id = 0
        user = None
        try:
            if guid and guid != '0000-0000':  # logged in state
                try:
                    user = CustomUserProfile.objects.get(guid=guid)  # check in profiles first
                    user = User.objects.get(id=user.user_id)
                except Exception as ex:
                    logger.exception("%s\t%s", "MyBookingsViewSet", ex)
                    try:
                        user = User.objects.get(username=guid)  # check in auth_user table
                    except Exception as exc:
                        user = None
                        logger.exception("%s\t%s", "getUserObject", exc)

            if user:
                user_id = user.id
            return user_id
        except Exception as ex:
            logger.exception("%s\t%s", "get_userid", ex)
            user_id = 0
            return user_id

    @staticmethod
    def get_cpurl(bookingid):
        """Get cancel policy hyperlink.
        this function returns urls.
        Returns: (string)
        """
        return 'https://' + settings.HOST + '/bus/getPolicyLink/%s/' % (bookingid)

    @staticmethod
    def get_ticket(pobj):
        """Get booking eticket url.
        this function returns urls.
        Returns: (string)
        """
        return 'https://' + settings.HOST + '/bus/eticket/%s/%s/%s/' % (pobj.bookingid, pobj.paymentid, '00')

    @staticmethod
    def get_traveller_details(pobj):
        """Get booking eticket url.
        this function returns urls.
        Returns: (string)
        """
        travellers_details = []
        bj = simplejson.loads(pobj.bookjson)
        title_map = {
            '0': 'Mr',
            '1': 'Mr',
            '2': 'Mrs',
            '3': 'Miss',
            '4': 'Master',
            '5': 'Miss',
        }
        for traveller in simplejson.loads(pobj.travellerdetails):
            traveler_details = dict()
            traveler_details['title'] = title_map[traveller['Title']]
            traveler_details['first_name'] = traveller['FirstName']
            traveler_details['last_name'] = traveller['LastName']
            if bj.get('row_type', '') == 'onwardflights':
                traveler_details['seat_number'] = traveller.get('OnwSeat', '')
            else:
                traveler_details['seat_number'] = traveller.get('RetSeat', '')
            traveler_details['age']=traveller['Age']
            traveler_details['email_id'] =traveller['Email']
            traveler_details['mobile_no'] = traveller['Mobile']
            travellers_details.append(traveler_details)
        return travellers_details

    @staticmethod
    def get_farebreakup(bjson=None, pobj=None):
        if pobj:
            bjson = simplejson.loads(pobj.bookjson)
        charges_dict = {'asn_amount': 0, 'basefee': 0, 'reservationFee': 0, 'tf': 0,
                        'toll': 0, 'bookingFee': 0, 'servicetax': 0, 'discount': 0, 'levy': 0,
                        'ServiceCharge': 0, 'OTHER_CHARGES': 0, 'TollFeeRajasthan':0, 'concession': 0}
        key_mapping_dict = {'BASIC_FARE': 'basefee', 'AsnFare': 'asn_amount', 'RESERVATION_FEE': 'reservationFee',
                            'TOTAL_FARE': 'tf', 'LEVIES_CHARGES': 'levy', 'TOLL_FEE': 'toll',
                            'SERVICE_TAX': 'servicetax', 'DISCOUNT': 'discount', 'CONCESSIONS_FEE': 'concession',
                            'ServiceCharge': 'ServiceCharge', 'SERVICE_FEE': 'ServiceCharge',
                            'OTHER_CHARGES': 'OTHER_CHARGES', 'TollFeeRajasthan': 'TollFeeRajasthan'}
        try:
            updatefare = bjson['BlockticketFareBreakup']
            #updatedfare = updatefare['updatedFare']
            fareBreakups = dict()
            if 'fareBreakup' in updatefare:
                fareBreakups = updatefare['fareBreakup']
            for item in fareBreakups.get('fareBreakups', {}):
                breakup = item.get('customerPriceBreakUp', {})
                for key in breakup:
                    k_name = key.get('componentName', '')
                    if k_name in key_mapping_dict:
                        charges_dict[key_mapping_dict[k_name]] += key['value']

        except Exception as e:
            logger.exception("%s\t%s\t%s", "Depot", "get_farebreakup", e)

        return charges_dict

    @staticmethod
    def get_payment_breakup(pobj):
        tax = bfare = 0
        (rfs, rfm) = MyBookings.get_rfs_rfm(pobj)
        bj = simplejson.loads(pobj.bookjson)
        charges_dict = MyBookings.get_farebreakup(bj)
        for seat in bj['seatsSelected']:
            tax += float(seat.get('stax', 0))
            bfare += float(seat.get('bfare', 0))
            seat['bfare'] = float(seat.get('bfare', 0))
        ypm = [
            {
                "k": "operator gst",
                "v": str(tax),
                "c": "INR"
            }, {
                "k": "base",
                "v": str(bfare),
                "c": "INR"
            }, {
                "k": "discount",
                "v": str(bj.get('promo', {}).get('promoDiscount', 0)),
                "c": "INR"
            }, {
                "k": "goCash+",
                "v": str(float(bj.get('credits_amount', 0)) - float(bj.get('vested_amount', 0))),
                "c": "INR"
            }, {
                "k": "credits",
                "v": str(bj.get('vested_amount', 0)),
                "c": "INR"
            }]
        for key in charges_dict:
            if key in ['asn_amount', 'bookingFee', 'levy', 'op_servicetax', 'reservationFee', 'toll', 'concession',
                       'ServiceCharge', 'OTHER_CHARGES', 'bookingFee', 'TollFeeRajasthan']:
                if charges_dict[key] > 0:
                    ypm.append({'k': key, 'v': str(int(charges_dict[key])), 'c': 'INR'})

        ypm_kafka = []
        for key in ypm:
            y = dict()
            y['key'] = key['k']
            y['value'] = key['v']
            y['currency'] = key['c']
            ypm_kafka.append(y)

        yps = {
            "k": "You Paid",
            "v": str(pobj.travelamount),
            "c": "INR",
        }

        yp = {
            "k": "You Paid",
            "v": str(pobj.travelamount),
            "c": "INR"
        }

        yps_kafka = {'key': yps['k'], 'value': yps['v'],'currency': yps['c']}

        if rfs == {}:

            rfs_kafka = list()
        else:
            rfs_kafka = [{'key': rfs['k'], 'value': rfs['v'], 'currency': rfs['c']}]
        rfm_kafka = []
        for key in rfm:
            r = dict()
            r['key'] = key['k']
            r['value'] = key['v']
            r['currency'] = key['c']
            rfm_kafka.append(r)

        yp_kafka = {'key': yp['k'],'value':yp['v'], 'currency':yp['c']}

        return rfs_kafka, rfm_kafka, ypm_kafka, yps_kafka, yp_kafka
