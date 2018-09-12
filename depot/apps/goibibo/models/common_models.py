# -*- coding: utf-8 -*-
"""Goibibo Database Django Models."""

from django.db import models
from django.utils.translation import ugettext_lazy as _
from .model_utils import ModelUtils

__all__ = ['RefundBreakup']
refund_breakup_model_utils_obj = ModelUtils("refundbreakup")
app_label_name = 'goibibo'


class RefundBreakup(models.Model):
    paymentid = models.CharField(max_length=100, db_index=True, blank=True)
    mihpayid = models.CharField(max_length=100, null=True, db_index=True, blank=True)
    refund = models.FloatField(default=0, null=False, blank=False)
    refund_type = models.CharField(max_length=100, blank=False,
                                   choices=(('cash', 'cash'), ('miles', 'miles'), ('credits', 'credits')))
    status = models.CharField(max_length=100, null=False, db_index=True, choices=(
    ('pending', 'pending'), ('refunded', 'refunded'), ('issue', 'issue'), ('to cancel', 'to cancel')))
    comments = models.TextField(blank=True)
    createdon = models.DateTimeField(auto_now_add=True)
    modifiedon = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class."""
        app_label = app_label_name
        db_table = refund_breakup_model_utils_obj.get_table_name("refundbreakup")
