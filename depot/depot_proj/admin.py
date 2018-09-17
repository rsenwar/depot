"""Depot Admin Site."""

from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from depot_proj import views as depot_views


class DepotAdminSite(admin.AdminSite):
    """Depot Admin Site Class."""

    def __init__(self, *args, **kwargs):
        """Initialize admin site."""
        super().__init__(*args, **kwargs)
        self._registry.update(admin.site._registry)
        self._actions = {}
        self._global_actions = {}

    def get_urls(self):
        """Return admin urls with extra urls."""
        urls = admin.site.get_urls()
        extra_urls = [
            path('create-user/', depot_views.create_user, name="admin-user-creation"),
            path('create-permissions-contenttypes/',
                 depot_views.create_permissions_content_types,
                 name="temp-permissions-contenttypes"),
            #path('add/<int:x>/<int:y>/', depot_views.add, name="temp-add"),

            path('favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico')),
        ]
        return urls + extra_urls


depot_admin_site = DepotAdminSite()
