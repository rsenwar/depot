"""Resource for my booking data."""
import logging
import simplejson
import re

from django.conf import settings
from apps.app_constants import bus_constants
from apps.app_helpers import utility
from apps.goibibo.src.list_bookings import ListBusBooking
#from apps.services.rewards.main import Rewards
from apps.goibibo.models.bus_models import PaymentDetails, CancelTicket
from apps.goibibo.models.common_models import RefundBreakup
from apps.goibibo.models.custom_user_models import CustomUserProfile, User
#from apps.goibibo.models.credits.CreditsHistory
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
                yield MyBookings.get_bus_booking_data(bb_obj)
            except Exception:
                smart_newrelic.push_transaction_exception()
                logger.exception("Exception in MyBookings.get_my_bookings_data")

    @staticmethod
    def get_bus_booking_data(queryset, user_id):
        """Get bus_booking details for a bus_booking object."""
        tax = bfare = fare = 0
        json_result = []
        for payobj in queryset:
            #rfs, refund_breakup = MyBookings.get_rfs_rfm(payobj)
            (rfs, rfm, ypm, yps, yp) = MyBookings.get_payment_breakup(payobj)
            travellerdetails = MyBookings.get_traveller_details(payobj)
            try:
                data = {}
                promoname = ''
                bj = simplejson.loads(payobj.bookjson)
                try:
                    if bj['DPName'] == -1:
                        bj['DPName'] = ''
                    else:
                        bj['DPName'] = str(bj['DPName'])
                except:
                    bj['DPName'] = ''
                    pass
                try:
                    dpname = bj.get('ConfirmTicket', {}).get('DPDetails', {}).get('DPName')
                    dptime = bj.get('ConfirmTicket', {}).get('DPDetails', {}).get('DPTime')
                except:
                    dpname = ''
                    dptime = bj['arrdate'].replace('Z', '')
                try:
                    bpcn = bj.get('ConfirmTicket', {}).get('BPDetails', '').get('BPContactNumber').split(',')
                    bpt = bj.get('ConfirmTicket', {}).get('BPDetails', '').get('BPTime')
                except:
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
                    fare = seat.get('fare', 0)
                    seat['bfare'] = float(seat.get('bfare', 0))
                tr = simplejson.loads(payobj.travellerdetails)
                if 'promo' in bj:
                    promoname = bj['promo'].get('promoname')
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
            except:
                data = {}
            if data != {}:
                json_result.append(data)
        return json_result



    @staticmethod
    def get_rfs_rfm(pay_obj):
        status_map = {"to deliver": "OK",
                      "to refund": "CANCELLED",
                      "pending": "CANCELLED",
                      "refunded": "CANCELLED",
                      "charged": "OK"
                      }
        refund_breakup = []
        rfs = {}
        gocash = gocashP = cash = credits = 0
        refund_breakupobj_map = {'cash': 0, 'credits': 0}
        if status_map.get(pay_obj.status, "OK") == 'CANCELLED':

            refund_breakupobj = RefundBreakup.objects.filter(paymentid=pay_obj.paymentid)
            gocash_refund_breakupobj = None
            get_refunded_gocash = MyBookings.get_refunded_gocash(pay_obj.paymentid)
            for breakupobj in gocash_refund_breakupobj:
                gocash += float(breakupobj.VestedAmount)
                gocashP += float(breakupobj.CreditsAmount) + float(breakupobj.BucketAmount)
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
        return 'https://' + settings.HOST + '/bus/getPolicyLink/%s/' % (bookingid)

    @staticmethod
    def get_ticket(pobj):
        return 'https://' + settings.HOST + '/bus/eticket/%s/%s/%s/' % (pobj.bookingid, pobj.paymentid, '00')

    @staticmethod
    def get_traveller_details(pobj):
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
        asn_amount = basefee = reservationFee = tf = toll = bookingFee = servicetax = discount = levy = 0
        ServiceCharge = OTHER_CHARGES = TollFeeRajasthan = concession = 0
        try:
            updatefare = bjson['BlockticketFareBreakup']
            updatedfare = updatefare['updatedFare']
            seats_breakup = []
            if 'fareBreakup' in updatefare:
                fareBreakups = updatefare['fareBreakup']
                for item in fareBreakups['fareBreakups']:
                    breakup = item['customerPriceBreakUp']
                    seat_breakup = {}
                    seat_breakup['seat'] = item['seatName']
                    for key in breakup:
                        if key['componentName'] == 'BASIC_FARE':
                            seat_breakup['bfare'] = key['value']
                            basefee += key['value']
                        elif key['componentName'] == 'AsnFare':
                            seat_breakup['asn'] = key['value']
                            asn_amount += key['value']
                        elif key['componentName'] == 'RESERVATION_FEE':
                            reservationFee += key['value']
                        elif key['componentName'] == 'TOTAL_FARE':
                            seat_breakup['fare'] = key['value']
                            tf += key['value']
                        elif key['componentName'] == 'LEVIES_CHARGES':
                            seat_breakup['levy'] = key['value']
                            levy += key['value']
                        elif key['componentName'] == 'TOLL_FEE':
                            seat_breakup['toll'] = key['value']
                            toll += key['value']
                        elif key['componentName'] == 'SERVICE_TAX':
                            seat_breakup['stax'] = key['value']
                            servicetax += key['value']
                        elif key['componentName'] == 'DISCOUNT':
                            seat_breakup['discount'] = key['value']
                            discount += key['value']
                        elif key['componentName'] == 'CONCESSIONS_FEE':
                            seat_breakup['conc'] = key['value']
                            concession += key['value']
                        elif key['componentName'] == 'ServiceCharge' or key['componentName'] == 'SERVICE_FEE':
                            ServiceCharge += key['value']
                        elif key['componentName'] == 'OTHER_CHARGES':
                            seat_breakup['oth_charge'] = key['value']
                            OTHER_CHARGES += key['value']
                        elif key['componentName'] == 'TollFeeRajasthan':
                            seat_breakup['tfraj'] = key['value']
                            TollFeeRajasthan += key['value']
                    seats_breakup.append(seat_breakup)
                for seat in bjson['seatsSelected']:
                    for item in seats_breakup:
                        if item['seat'] == seat['seat']:
                            seat['fare'] = item['fare']
                            seat['bfare'] = item['bfare']
        except Exception as e:
            logger.exception("%s\t%s\t%s", "Depot", "get_farebreakup", e)

        return (asn_amount, basefee, reservationFee, tf, toll, servicetax, discount, concession, ServiceCharge,
                OTHER_CHARGES,bookingFee, TollFeeRajasthan, levy)

    @staticmethod
    def get_payment_breakup(pobj):
        tax = bfare = fare = 0
        (rfs, rfm) = MyBookings.get_rfs_rfm(pobj)
        bj = simplejson.loads(pobj.bookjson)
        (asn_amount, basefee, reservationFee, tf, toll, op_servicetax, discount, concession, ServiceCharge,
         OTHER_CHARGES, bookingFee, TollFeeRajasthan, levy) = MyBookings.get_farebreakup(bj)
        for seat in bj['seatsSelected']:
            tax += float(seat.get('stax', 0))
            bfare += float(seat.get('bfare', 0))
            fare = seat.get('fare', 0)
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

        for item in ['asn_amount', 'bookingFee', 'levy', 'op_servicetax', 'reservationFee', 'toll', 'concession',
                     'ServiceCharge', 'OTHER_CHARGES', 'bookingFee', 'TollFeeRajasthan']:
            if eval(item) > 0:
                ypm.append({'k': item, 'v': str(eval(item)), 'c': 'INR'})

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

        yps_kafka = {'key':yps['k'], 'value':yps['v'],'currency': yps['c']}

        if rfs == {}:

            rfs_kafka = []
        else:
            rfs_kafka = [{'key': rfs['k'], 'value': rfs['v'], 'currency': rfs['c']}]

        rfm_kafka = []
        for key in rfm:
            r = {}
            r['key'] = key['k']
            r['value'] = key['v']
            r['currency'] = key['c']
            rfm_kafka.append(r)

        yp_kafka = {'key': yp['k'],'value':yp['v'], 'currency':yp['c']}

        return rfs_kafka, rfm_kafka, ypm_kafka, yps_kafka, yp_kafka
