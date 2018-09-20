"""
Module to be used to test apis
http://www.django-rest-framework.org/api-guide/testing/
"""
import pytest
# from django.urls import reverse
from rest_framework.test import APIRequestFactory, APIClient
from apps.apis.my_bookings.views import MyBookingsViewSet
from apps.app_constants import bus_constants



@pytest.mark.django_db
def test_viewset_client_user():
    client = APIClient()
    url = '/apis/v1/my-bookings/'
    data = dict(page_size=1, page=2, u_id=13, all=1, secret=bus_constants.MYBOOKING_TOKEN)
    response = client.get(url, data)
    assert response.status_code == 200
    assert response.data['count'] == 3
    assert len(response.data['data']) == 1
    assert response.data['links']['next'] is not None
    assert response.data['links']['previous'] is not None


@pytest.mark.django_db
def test_viewset():
    factory = APIRequestFactory()
    url = '/apis/v1/my-bookings/'
    data = {'pid': 'GOBUS8c0bfb18b2', 'secret': bus_constants.MYBOOKING_TOKEN}
    request = factory.get(url, data)
    view = MyBookingsViewSet.as_view({'get': 'list'})
    response = view(request)
    assert response.status_code == 200
    assert response.data['count'] == 1
    assert len(response.data['data']) == 1
    assert response.data['data'][0]['payment_id'] == 'GOBUS8c0bfb18b2'


@pytest.mark.django_db
def test_viewset_client_user_not_all():
    client = APIClient()
    url = '/apis/v1/my-bookings/'
    data = dict(page_size=10, page=1, u_id=13, secret=bus_constants.MYBOOKING_TOKEN)
    response = client.get(url, data)
    #import pdb;pdb.set_trace()
    assert response.status_code == 200
    assert response.data['count'] == 3
    assert len(response.data['data']) == 3
    assert response.data['links']['next'] is None
    assert response.data['links']['previous'] is None


@pytest.mark.django_db
def test_viewset_client_user_not_all_failure():
    client = APIClient()
    url = '/apis/v1/my-bookings/'
    data = dict(page_size=5, page=2, u_id=18, secret=bus_constants.MYBOOKING_TOKEN)
    response = client.get(url, data)
    assert response.status_code == 404
    assert response.data['count'] == 0
    assert len(response.data['data']) == 0
    assert response.data['links']['next'] is None
    assert response.data['links']['previous'] is None


if __name__ == "__main__":
    pytest.main()
