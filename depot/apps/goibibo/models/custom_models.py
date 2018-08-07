# -*- coding: utf-8 -*-
"""Goibibo Database Django Models."""
from django.contrib.contenttypes.models import ContentTypeManager
from django.contrib.sites.models import _simple_domain_name_validator, SiteManager
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .model_utils import ModelUtils

__all__ = ['CustomSite', 'CustomContentType']
profile_model_utils_obj = ModelUtils("profiles")
app_label_name = 'goibibo'


class CustomContentType(models.Model):
    """CustomContent Type- Model for old django_content_type.
    have removed a lot of inbuilt functions like
    model_class()
    get_objects_for_this_type()
    get_all_objects_for_this_type()
    for more info refer django content type source code
    https://github.com/django/django/blob/master/django/contrib/contenttypes/models.py
    """

    name = models.CharField(max_length=100)
    app_label = models.CharField(max_length=100)
    model = models.CharField(_('python model class name'), max_length=100)
    objects = ContentTypeManager()

    # class Meta:
    #     verbose_name = _('content type')
    #     verbose_name_plural = _('content types')
    #     db_table = 'django_content_type'
    #     unique_together = (('app_label', 'model'),)

    def __str__(self):
        """Return string representation."""
        return self.name

    def natural_key(self):
        """Return natural key as tuple of (app_lable, model)."""
        return self.app_label, self.model

    class Meta:
        """Meta class."""

        app_label = app_label_name
        db_table = "django_content_type"


class CustomSite(models.Model):
    """Custom Django_site."""

    domain = models.CharField(_('domain name'), max_length=100,
                              validators=[_simple_domain_name_validator])
    name = models.CharField(_('display name'), max_length=50)
    objects = SiteManager()

    class Meta:
        """Meta class."""

        db_table = 'django_site'
        verbose_name = _('site')
        verbose_name_plural = _('sites')
        ordering = ('domain',)
        app_label = app_label_name

    def __str__(self):
        """Return string representation."""
        return self.domain