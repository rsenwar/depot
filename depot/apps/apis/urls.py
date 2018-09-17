"""Depot APIs' urls."""

from django.urls import re_path, include, path
from rest_framework import routers

from apps.apis.my_bookings import views as my_bookings_views

router = routers.DefaultRouter()

router.register('my-bookings', my_bookings_views.MyBookingsViewSet, base_name='my-bookings')

urlpatterns = [
    re_path(r'^(?P<version>(v1))/', include(router.urls)),
    path('my-bookings-kafka/', my_bookings_views.MyBookingsKafka.as_view(), name='my-bookings-kafka-push')
]
