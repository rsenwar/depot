# -*- coding: utf-8 -*-
"""Goibibo Database Hotels Models."""

# from django.contrib.contenttypes.fields import GenericRelation
import datetime
from django.db import models

from apps.app_constants import bus_models_choices as bus_choices
# from .common_models import ItemNotes
from apps.goibibo.models.custom_models import CustomSite
from apps.goibibo.models.model_utils import ModelUtils
from apps.goibibo.models.custom_user_models import User

model_utils_obj = ModelUtils("bus")

__all__ = []


class CommonModel(models.Model):
    comments = models.TextField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_by = models.ForeignKey(User, null=True, blank=True,
                                    on_delete=models.DO_NOTHING,
                                    limit_choices_to={'is_active': True, 'is_staff': True})

    class Meta:
        """Meta class."""

        abstract = True



