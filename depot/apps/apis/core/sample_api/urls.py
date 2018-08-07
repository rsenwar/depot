"""Sample API URLs."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.apis.core.sample_api import sample_api as sample_views

router = DefaultRouter()
router.register(r'sample2', sample_views.SampleViewSet, base_name='sample2')

urlpatterns = [
    path('sample/', sample_views.api_root, name='sample-root'),
    path('sample/hello/', sample_views.hello_world, name='sample-hello'),
    path('sample/list/', sample_views.sample_list, name='sample-list'),
]

urlpatterns += [
    path('', include(router.urls))
]
