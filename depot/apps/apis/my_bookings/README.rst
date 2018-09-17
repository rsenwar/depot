============
My Bookings
============

How To Edit The Code:
---------------------

1. Add the field to methods apps.apis.my_bookings.resources::

        def get_bus_booking_data(queryset, user_id):
            .
            .
            data['<new key>'] = bj.get('<new key>', '<default value>')

2. Add the field in serializer file apps.apis.my_bookings.serializer.::

        class MyBookingSerializer...
            .
            .
            is_test_booking = serializers.NullBooleanField()

3. Add the field in proto file apps/apis/my_bookings/busProtobuff.proto.::

        message BusMyBookingData{
            .
            .
            bool is_test_booking = 45;      // whether test_booking or not
        }


Notes:
    .. _Note1:

    1. Choose your function carefully and update the testcases for the updated function.
    2. Update the proto compiled file::

        protoc --python_out=. busProtobuff.proto

