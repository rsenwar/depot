"""depot_proj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework.authtoken import views as auth_token_views
from rest_framework.documentation import include_docs_urls
from rest_framework_swagger.views import get_swagger_view

from depot_proj import views as depot_views
from depot_proj.admin import depot_admin_site

STATIC_PATH = settings.STATIC_ROOT

schema_view = get_swagger_view(title='Depot API Docs')

my_booking_urlpatterns = [
    path('apis/', include('apps.apis.urls')),
]
api_token_auth_urls = [
    path('api-token-auth/', auth_token_views.obtain_auth_token),
]
'''
urlpatterns = [
    #path('docs/', schema_view, name='swagger-docs'),
    #path('', depot_views.index, name="depot_index"),
    path('', depot_views.IndexView.as_view(), name="depot_index"),
    path('sample_api/', include('apps.apis.core.sample_api.urls')),
    #path('sample_api/', include('apps.apis.core.sample_api.urls')),
    #path('admin/', depot_admin_site.urls),
    #path('accounts/', include('django.contrib.auth.urls')),
    #path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    #path('my-stay-api/docs/', include_docs_urls(
    #    title='Depot My Booking API', patterns=my_stay_urlpatterns + api_token_auth_urls,
    #    public=False)),
    #path('favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico')),
]
'''

urlpatterns = my_booking_urlpatterns + api_token_auth_urls + [
    path('docs/', schema_view, name='swagger-docs'),
    path('', depot_views.IndexView.as_view(), name="depot_index"),
    #path('sample_api/', include('apps.apis.core.sample_api.urls')),
    path('admin/', depot_admin_site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    #path('my-booking-api/docs/', include_docs_urls(
    #    title='Depot My Booking API', patterns=my_booking_urlpatterns + api_token_auth_urls,
    #    public=False)),
    path('favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico')),
]


if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
