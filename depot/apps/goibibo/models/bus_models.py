# -*- coding: utf-8 -*-
"""Goibibo Database Hotels Models."""

from django.contrib.contenttypes.fields import GenericRelation
import datetime
import re
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import models
from apps.goibibo.models.multifield import MultiSelectField

from apps.app_constants import bus_models_choices as bus_choices
from apps.app_constants import bus_constants
# from .common_models import ItemNotes
from apps.goibibo.models.custom_models import CustomSite
from apps.goibibo.models.model_utils import ModelUtils
from apps.goibibo.models.custom_user_models import User

model_utils_obj = ModelUtils("bus")

__all__ = ['PaymentDetails', 'CancelTicket', 'busConfigParam']


def validate_name(value):
    p = re.compile('^[.a-zA-Z\s]+$')
    if not p.match(value):
        raise ValidationError(u'%s is not a valid name component' % value)


def validate_mobile(value):
    p = re.compile(r'^[0-9]{10}$')
    if not p.search(value):
        msg = u"Invalid mobile number."
        raise ValidationError(msg)


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


class PaymentDetails(models.Model):
    guid = models.CharField(db_index=True,max_length=100)
    firstname = models.CharField(max_length=50,null=False, validators=[validate_name])
    lastname = models.CharField(max_length=50,null=True, blank=True)
    address = models.TextField(null=True)
    city = models.CharField(max_length=30,null=False)
    pincode = models.CharField(max_length=30,null=True,blank=True)
    state = models.CharField(max_length=30,null=True, blank=True)
    country = models.CharField(max_length=30,null=True, blank=True)
    mobile = models.CharField(max_length=30,null=True, validators=[validate_mobile])
    landline = models.CharField(max_length=30,null=True,blank=True)
    email = models.EmailField(null=False,db_index=True, validators=[validate_email])
    travellerdetails = models.TextField(null=False)
    source = models.CharField(max_length=100,null=False)
    dest = models.CharField(max_length=100,null=False)
    bookingdate = models.DateTimeField(auto_now_add=True)
    departuredate = models.DateTimeField(null=False,db_index=True)
    arrivaldate = models.DateTimeField(null=False,db_index=True)
    status = models.CharField(max_length=50, choices=bus_choices.STATUS_CHOICES)
    bookingflag = models.BooleanField(null=False, default=None)
    bookingid = models.CharField(max_length=100,null=True,blank=True,db_index=True)
    mihpayid = models.CharField(max_length=100,null=True,db_index=True,blank=True)
    paymentid = models.CharField(max_length=100,null=False,db_index=True)
    travelamount = models.FloatField(null=False,db_index=True)
    bookjson = models.TextField()
    bstatus = models.IntegerField(default=0,null=False,blank=False)
    # Commented below choices for displaying partner detail
    #booking_type_choices = (
    #    ('O', 'Online'),
    #    ('P', 'Package')
    #)

    booking_type = models.CharField(
        max_length=128, default='O', db_index=True, blank=True)

    class Meta:
        app_label = model_utils_obj.get_app_name()
        db_table = model_utils_obj.get_table_name("paymentdetails")

    def __str__(self):
        return str(self.paymentid)

class CancelTicket(models.Model):
    cancelid = models.ForeignKey(PaymentDetails,limit_choices_to={'bookingflag':True}, on_delete=models.DO_NOTHING)
    cancelref = models.CharField(max_length=20,null=True,blank=True)
    guid = models.CharField(db_index=True,max_length=50)
    canceltime = models.DateTimeField(auto_now=True)
    cancelamount = models.FloatField(null=False)
    cancelrefundamount = models.FloatField(null=True,blank=True)
    cancelpnr = models.CharField(max_length=20,null=True,db_index=True)
    cancelbookingid = models.CharField(max_length=100,null=True,db_index=True)
    cancelstatus = models.CharField(max_length=100, null=False, db_index=True, choices=bus_choices.CANCEL_CHOICES,)
    reason = models.CharField(max_length=1,null=True,choices=bus_choices.REASON_CHOICES, default='5')
    cancelmihpayid = models.CharField(max_length=100,null=True,db_index=True)
    seats = MultiSelectField(max_length=500,choices=(('------','------'),), blank=True)
    partial = models.BooleanField(default=False)
    createdOn = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(null=True,blank=True)
    modifiedBy = models.CharField(max_length=200,null=True,blank=True)
    vendorcharges = models.FloatField(null=True,blank=True)
    ibibocharges = models.FloatField(default=bus_constants.IBIBO_BUS_CANCELLATION_CHARGES)
    if_autocancel = models.BooleanField(default=False)

    # history = historymodels.HistoricalRecords()

    class Meta:
        app_label = model_utils_obj.get_app_name()
        db_table = model_utils_obj.get_table_name("cancelticket")

    def __unicode__(self):
        return u"%s" % self.cancelbookingid


class busConfigParam(CommonModel):
    config_key = models.CharField(max_length=100,db_index=True)
    config_value = models.TextField()
    active = models.BooleanField(default=True)
    environment_type = models.IntegerField(default = 1, choices=bus_choices.ENV_CHOICES)
    modifiedOn = models.DateTimeField(auto_now=True)
    createdOn = models.DateTimeField(db_index=True, auto_now_add=True)
    modifiedby = models.CharField(max_length=200,null=True,blank=True)

    class Meta:
        """Meta class."""

        app_label = model_utils_obj.get_app_name()
        db_table = model_utils_obj.get_table_name("busconfigparam")

    #def __str__(self):
    #    """Return string representation."""
    #    return '{}@{}'.format(self.config_key, self.get_environment_type_display())
