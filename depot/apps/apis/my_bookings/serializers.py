"""MyBooking Serializers."""
# pylint: disable=abstract-method
from rest_framework import serializers


class MyBookingSerializer(serializers.Serializer):
    status = serializers.CharField()
    payment_id = serializers.CharField()
    pnr = serializers.CharField()
    db_primary_id = serializers.CharField()
    booking_refrence = serializers.CharField()
    user_id = serializers.CharField()
    travell_start_date_time = serializers.CharField()
    travell_stop_date_time = serializers.CharField()
    ticket_booked_date_time = serializers.CharField()
    source_city_name = serializers.CharField()
    destination_city_name = serializers.CharField()
    source_city_voyager_id = serializers.CharField()
    destination_city_voyager_id = serializers.CharField()
    travell_duration = serializers.CharField()
    bus_type = serializers.CharField()
    mobile_ticket = serializers.CharField()
    tracking_enabled = serializers.CharField()
    boarding_point_name = serializers.CharField()
    departure_point_name = serializers.CharField()
    boarding_point_time = serializers.CharField()
    arrival_point_name = serializers.CharField()
    cancellation_policy_url = serializers.CharField()
    privacy_flag = serializers.IntegerField()
    traveller_name = serializers.CharField()
    ugcId = serializers.CharField()
    is_ticket_refundable = serializers.BooleanField()
    is_ticket_cancellable = serializers.BooleanField()
    ticket_type = serializers.CharField()
    email_id = serializers.CharField()
    mobile = serializers.CharField()
    booking_id = serializers.CharField()
    print_pdf_url = serializers.CharField()
    bus_operator_name = serializers.CharField()
    amenities = serializers.ListField()
    boarding_point_contact_number = serializers.ListField()
    seat_selected = serializers.ListField()
    traveller_details = serializers.ListField()
    refund_summary = serializers.JSONField()
    refund_summary_breakup = serializers.ListField()
    amount_paid_summary = serializers.JSONField()
    amount_paid_breakup = serializers.ListField()
    amount_paid = serializers.JSONField()
    business_flag = serializers.IntegerField()
    boarding_point_time = serializers.CharField()
    arrival_point_name = serializers.CharField()
