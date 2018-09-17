"""MyBooking API View."""
import logging
import traceback
from collections import OrderedDict

import coreapi
import coreschema

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse, QueryDict
from django.views import View
from rest_framework import viewsets, pagination, versioning, status as drf_status
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.request import clone_request
from rest_framework.schemas import AutoSchema
from rest_framework.decorators import action


from apps.apis.core.proto import ProtoAPIView, ProtoRenderer
from apps.apis.my_bookings.resources import MyBookings
from apps.apis.my_bookings.mybooking_pb2 import BusMyBookingApiData
from apps.apis.my_bookings.permissions import MyBookingsPermission

from apps.apis.my_bookings.serializers import MyBookingSerializer
from apps.app_helpers import kafka_helper
from apps.goibibo.models import PaymentDetails, User, CustomUserProfile
from apps.app_constants import bus_constants

from lib import smart_newrelic, smartjson

logger = logging.getLogger(__name__)
# MY_BOOKINGS_MIDDLEWARE_KAFKA = "BUS_MYBOOKING_PROTOBUF_DATA_DEPOT"
MY_BOOKINGS_MIDDLEWARE_KAFKA = "BUS_MYBOOKING_PROTOBUFF_DATA"
# MY_BOOKINGS_MIDDLEWARE_KAFKA_F1 = "BUS_MYBOOKING_PROTOBUF_DATA_DEPOT"
MY_BOOKINGS_MIDDLEWARE_KAFKA_F1 = 'MYBOOKINGS_BUS'


class MyBookingsViewSchema(AutoSchema):
    """My stays schema."""

    version = coreapi.Field(
        "version", required=True, location="path",
        schema=coreschema.String(description="Version Number", default="v1"),
        description="Version Number", example="v1", type='string')
    booking_ref = coreapi.Field(
        "booking_ref", required=False, location="query",
        schema=coreschema.String(description="a speific bookingid or paymentid",
                                 default="GOHTLDANDSOMETHG"),
        description="a speific bookingid or paymentid", example="GOHTLDANDSOMETHG or HTLSOMETHNG",
        type='string')
    user_id = coreapi.Field(
        "user_id", required=False, location="query",
        schema=coreschema.String(description="user id for the user",
                                 default="234567667"),
        description="user id for the user", example="341241232", type='string')
    mobile = coreapi.Field(
        "mobile", required=False, location="query",
        schema=coreschema.String(description="mobile of the given user",
                                 default="8130780880"),
        description="mobile of the given user", example="8130780880", type='string')
    all = coreapi.Field(
        "all", required=False, location="query",
        schema=coreschema.String(description="for all type of booking status.",
                                 default="0"),
        description="for all type of booking status.", example="0", type='int')
    format = coreapi.Field(
        'format', required=False, location="query",
        schema=coreschema.String(description="format for response.", default='json'),
        description="format for response.", example='json', type='String')
    push_format = coreapi.Field(
        "push_format", required=False, location="query",
        schema=coreschema.String(description="format for data to be pushed on kafka topic.",
                                 default="proto"),
        description="format for data to be pushed on kafka topic.", example="proto",
        type='string')

    def get_manual_fields(self, path, method):
        """Add per-path fields."""
        extra_fields = []
        if path == '/apis/{version}/my-bookings/':
            extra_fields = [self.version, self.format, self.booking_ref, self.user_id,
                            self.mobile, self.all]
        elif path == '/apis/{version}/my-bookings/kafka-push/':
            extra_fields = [self.version, self.booking_ref, self.format, self.push_format]

        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields


class MyBookingsPagination(pagination.PageNumberPagination):
    """MyStays Pagination."""

    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 25

    def get_paginated_response(self, data):
        """Get paginated response."""
        return Response(OrderedDict([
            ('success', True),
            ('error', ''),
            ('count', self.page.paginator.count),
            ('links', OrderedDict([
                ('next', self.get_next_link()),
                ('previous', self.get_previous_link())
            ])),
            ('data', data)
        ]))


class MyBookingsViewSet(viewsets.GenericViewSet, ProtoAPIView):
    """My-stays My-booking.

    My Stays list view for a given user_id, mobile or booking_ref.

    * Requires token authentication.
    * Only active users are able to access this view.

    """

    # pylint: disable=too-many-ancestors
    proto_model = BusMyBookingApiData
    use_proto_model_in_exc = True
    serializer_class = MyBookingSerializer
    pagination_class = MyBookingsPagination
    renderer_classes = (JSONRenderer, ProtoRenderer)
    versioning_class = versioning.URLPathVersioning
    authentication_classes = (TokenAuthentication,)
    permission_classes = (MyBookingsPermission,)
    ordering = '-departuredate'

    #from bus.bus_Protobuf import *

    schema = MyBookingsViewSchema()

    def list(self, request, *args, **kwargs):
        """Return a list of existing bookings.

        Returns a list of all the existing bookings for the user specified by
        `user_id` and `mobile` or `booking_ref`.

        Returns: (dict)
        .. code-block:: json

            {
                "success": true,
                "error": "error message",
                "count": "no_of_results",
                "links": {
                    "next": "link_next_page",
                    "previous": "link_prev_page"
                },
                "data": [
                    "booking1",
                    "booking2",
                ]
            }

        Notes:
            For clients to authenticate, the token key should be included in
            the Authorization HTTP header. The key should be prefixed by the
            string literal "Token", with whitespace separating the two strings.

            Example:
                Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b

        """
        # pylint: disable=useless-super-delegation
        smart_newrelic.capture_request_params()
        user_id = request.GET.get('u_id', 0)
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            page = self.my_bookings_data_from_queryset(page, user_id=user_id)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response((serializer.data))

        queryset = self.my_bookings_data_from_queryset(queryset, user_id=user_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @staticmethod
    def my_bookings_data_from_queryset(queryset, **kwargs):
        """Get my_bookings data from queryset."""
        return MyBookings.get_bus_booking_data(queryset, **kwargs)

    @staticmethod
    def my_bookings_data(payobj):
        """Get my_bookings data from queryset."""
        return MyBookings.get_bus_booking_data(payobj)

    def handle_exception(self, exc):
        """Handle any exception that occurs."""
        response = super().handle_exception(exc)
        if 'detail' in response.data:
            data_exc = OrderedDict([
                ('api_status', False),
                ('api_error', response.data.pop('detail', '')),
                ('count', 0),
                ('links', OrderedDict([
                    ('next', None),
                    ('previous', None)
                ])),
                ('data', [])
            ])
            response.data = data_exc
        return response

    def get_queryset(self):  # noqa: C901 pylint: disable=too-many-branches
        """Return queryset for request parameters.

        Returns:
            (queryset)

        """
        queryset = PaymentDetails.objects.none()
        query_params = dict(self.request.query_params.items())
        #if not 'page' in query_params:
        #    query_params['page'] = 0
        #if not 'page_size' in query_params:
        #    query_params['page'] = settings.page_size
        exclude_status = ['new']
        all_bookings = query_params.get('all_bookings', 'false')
        if all_bookings == "true":
            exclude_status = []
        u_id = query_params.get('u_id', 0)
        p_id = query_params.get('pid', 0)
        mobile = query_params.get('mobile', '')
        secret_key = query_params.get('secret', '')
        if p_id:
            exclude_status = []
        try:
            if secret_key == 'Zx4T':
                if p_id:
                    queryset = PaymentDetails.objects \
                        .filter(Q(bookingid=p_id) | Q(paymentid=p_id)) \
                        .exclude(status__in=exclude_status) \
                        .order_by('-departuredate')
                    if not queryset:
                        queryset = PaymentDetails.objects \
                            .filter(Q(bookingid=p_id) | Q(paymentid=p_id)) \
                            .exclude(status__in=exclude_status) \
                            .order_by('-departuredate').using('goibibo_master')
                elif u_id:
                    # Get GUID from u_id and mobile
                    guid_list = []
                    user_queryset = User.objects.filter(id=u_id)
                    profile_queryset = CustomUserProfile.objects \
                        .filter(user_id=u_id)
                    if user_queryset:
                        # pylint: disable=unsubscriptable-object
                        guid_list.append(user_queryset[0].username)
                    if profile_queryset:
                        if profile_queryset[0].guid:
                            guid_list.append(profile_queryset[0].guid)
                    if mobile:
                        mobile_with_cc = '91' + mobile
                        queryset = PaymentDetails.objects \
                            .filter(Q(guid__in=guid_list) | Q(mobile=mobile) |
                                    Q(mobile=mobile_with_cc)) \
                            .exclude(status__in=exclude_status).order_by('-departuredate')
                    else:
                        queryset = PaymentDetails.objects \
                            .filter(guid__in=guid_list) \
                            .exclude(status__in=exclude_status).order_by('-departuredate')
        except Exception as ex:
            logger.exception("%s\t%s", "MyBookingsViewSet", ex)
            if settings.DEBUG:
                traceback.print_exc()

        if not queryset:
            logger.info("raising exception")
            # raise ParseError("request parameters are not correct.")

        return queryset

    def clone_my_sbookings_request_kafka_push(self, request):
        """Clone my stays request kafka push."""
        request_new = clone_request(request, 'GET')
        push_format = request.GET.get('push_format', 'proto')
        new_get_data = QueryDict('', mutable=True)
        new_get_data.update(request.GET)
        new_get_data['format'] = push_format
        request_new._request.GET = new_get_data   # pylint: disable=protected-access
        request_new.GET = new_get_data
        request_new.accepted_renderer, request_new.accepted_media_type = None, None
        neg = self.perform_content_negotiation(request_new, force=True)
        request_new.accepted_renderer, request_new.accepted_media_type = neg
        return request_new

    @action(detail=False, methods=['GET'], url_path='kafka-push')
    def push_proto_to_kafka(self, request, version, *args, **kwargs):
        """Push to kafka for mybookings - default:(proto).

        Returns a list of all the existing bookings for the user specified by
        `booking_ref` and format to push in kafka can be passed with parameter push_format.

        Args:
            request:
            version:

        Returns: (dict)
        ..

            {
                'data': 'data pushed to kafka',
                'success': True
            }

        """
        msg = {'success': False}
        booking_ref = request.GET.get('booking_ref')
        if booking_ref:
            request_new = self.clone_my_bookings_request_kafka_push(request)
            list_resp = self.list(request_new, version, *args, **kwargs)
            final_resp = self.finalize_response(request_new, list_resp, *args, **kwargs)
            status_code = final_resp.status_code
            if status_code == drf_status.HTTP_200_OK:
                resp = kafka_helper.push_to_kafka_asynchronous(MY_BOOKINGS_MIDDLEWARE_KAFKA,
                                                               final_resp.rendered_content)
                logger.info("Bus protobuf push to kafka hit %s for new topic %s status %s",
                            booking_ref, MY_BOOKINGS_MIDDLEWARE_KAFKA, resp)
                msg['data'] = "data push to kafka status %s." % resp
                msg['success'] = True
            else:
                logger.info("Bus protobuf push to kafka hit %s for new topic %s status %s",
                            booking_ref, MY_BOOKINGS_MIDDLEWARE_KAFKA, "failed-response")
                msg['data'] = "data not pushed to kafka status."

        else:
            logger.info("Bus protobuf push to kafka hit %s for new topic %s status %s",
                        booking_ref, MY_BOOKINGS_MIDDLEWARE_KAFKA, "failed - bad request")
            msg = {'data': "Please provide booking reference."}
            status_code = drf_status.HTTP_400_BAD_REQUEST

        return Response(data=msg, status=status_code)

    @action(detail=False, methods=['GET'], url_path='kafka-push-f1',
            renderer_classes=[JSONRenderer, ])
    def push_to_kafka_f1(self, request, version, *args, **kwargs):
        """Push to MYBOOKINGS_HOTELS kafka.

        Args:
            request:
            version:
            *args:
            **kwargs:

        Returns:

        """
        push_topic_name = MY_BOOKINGS_MIDDLEWARE_KAFKA_F1
        msg = {'success': False}
        push_to_kafka = int(request.GET.get('push_to_kafka', '1'))
        smart_newrelic.capture_request_params()
        queryset = self.get_queryset()
        data = list(MyBookings.get_my_bookings_data_f1(queryset))
        if push_to_kafka:
            userid = ''
            if data:
                userid = str(data[0].get('userid', ''))
                data = smartjson.dumps(data)
            resp = kafka_helper.push_to_kafka_asynchronous(push_topic_name, data, key=userid)
            msg['data'] = "data push to kafka status %s" % resp
            msg['success'] = True
        else:
            msg = data
        return Response(msg)


class MyBookingsBackwardViewSet(MyBookingsViewSet):
    """My Bookings Backward compatibility viewset.

    * Requires token for verification of the user.

    """

    # pylint: disable=too-many-ancestors
    renderer_classes = [ProtoRenderer, JSONRenderer]

    def clone_search_booking_request(self, request):
        """Clone request searchbookingv4."""
        request_new = clone_request(request, "GET")
        data = QueryDict('', mutable=True)
        params = dict(request.GET.items())
        if 'u_id' in params:
            data['user_id'] = params['u_id']
        if 'p_id' in params:
            data['booking_ref'] = params.get('p_id')
        if 'pagination' in params:
            data['page_size'] = params['pagination']
        if 'page_no' in params:
            data['page'] = params['page_no']
        if 'mobile' in params:
            data['mobile'] = params['mobile']
        if 'all_bookings' in params and params['all_bookings'] == 'true':
            data['all'] = 1
        data['format'] = params.get('format', 'proto')

        request_new.GET = data
        request_new._request.GET = data     # pylint: disable=protected-access

        neg = self.perform_content_negotiation(request_new, force=True)
        request_new.accepted_renderer, request_new.accepted_media_type = neg
        return request_new

    def list(self, request, *args, **kwargs):
        """Search booking v4.

        Args:
            request:
            version:
            *args:
            **kwargs:

        Returns:

        """
        u_id = request.GET.get('u_id')
        if u_id:
            request_token = request.GET.get('secret')
            if request_token != bus_constants.MYBOOKING_TOKEN:
                raise ValidationError({'detail': 'Please provide token for validation'})
        request_new = self.clone_search_booking_request(request)
        return super().list(request_new, *args, **kwargs)


class MyBookingsKafka(View):
    """My Bookings Kafka push."""

    def get(self, request):     # pylint: disable=no-self-use
        """Push to kafka my booking details.

        Args:
            request:

        Parameters:
            booking_ref: bookign reference - bookingid or paymentid (required)
            version: version of my-stays API. (default: v1)
            format: format data to be pushed. (default: proto)

        Returns:

        """
        booking_ref = request.GET.get('booking_ref')
        resp_format = request.GET.get('format', 'proto')
        if booking_ref:
            # data = {'booking_ref': booking_ref, 'format': resp_format}
            mybookings_list = MyBookingsViewSet.as_view({'get': 'list'})(request)
            if resp_format == 'proto':
                proto_renderer_obj = ProtoRenderer()
                proto_renderer_obj.proto_model = BusMyBookingApiData
                response = proto_renderer_obj.render(mybookings_list.data)
            else:
                response = JSONRenderer().render(mybookings_list.data)
            if mybookings_list.status_code == 200:
                resp = kafka_helper.push_to_kafka_asynchronous(MY_BOOKINGS_MIDDLEWARE_KAFKA,
                                                               response)
                logger.info("Hotels protobuf push to kafka hit %s for new topic %s status %s",
                            booking_ref, MY_BOOKINGS_MIDDLEWARE_KAFKA, resp)
                msg = "data push to kafka status %s." % resp
                status_code = drf_status.HTTP_200_OK
            else:
                logger.info("Hotels protobuf push to kafka hit %s for new topic %s status %s",
                            booking_ref, MY_BOOKINGS_MIDDLEWARE_KAFKA, "failed-response")
                msg = mybookings_list.data
                status_code = mybookings_list.status_code
        else:
            logger.info("Hotels protobuf push to kafka hit %s for new topic %s status %s",
                        booking_ref, MY_BOOKINGS_MIDDLEWARE_KAFKA, "failed - bad request")
            msg = "Please provide booking reference."
            status_code = drf_status.HTTP_400_BAD_REQUEST

        return HttpResponse(msg, status=status_code)
