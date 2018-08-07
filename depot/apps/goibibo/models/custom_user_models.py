"""Custom user models."""
from django.contrib import auth
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager, GroupManager, PermissionManager, \
    _user_get_all_permissions, _user_has_perm, _user_has_module_perms
from django.core import validators
from django.core.mail import send_mail
from django.db import models
from django.utils import six, timezone
from django.utils.translation import gettext_lazy as _

from .custom_models import CustomContentType
from .model_utils import ModelUtils

__all__ = ['User', 'CustomUserProfile']

profile_model_utils_obj = ModelUtils("profiles")
app_label_name = 'goibibo'


class Permission(models.Model):
    """Permission class."""

    name = models.CharField(_('name'), max_length=50)
    content_type = models.ForeignKey(
        CustomContentType,
        models.DO_NOTHING,
        verbose_name=_('custom content type'),)
    codename = models.CharField(_('codename'), max_length=100)
    objects = PermissionManager()

    class Meta:
        verbose_name = _('permission')
        verbose_name_plural = _('permissions')
        unique_together = (('content_type', 'codename'),)
        ordering = ('content_type__app_label', 'content_type__model',
                    'codename')
        app_label = app_label_name
        db_table = "auth_permission"
        managed = False

    def __str__(self):
        return "%s | %s | %s" % (
            six.text_type(self.content_type.app_label),
            six.text_type(self.content_type),
            six.text_type(self.name))

    def natural_key(self):
        return (self.codename,) + self.content_type.natural_key()
    natural_key.dependencies = ['contenttypes.contenttype']


class Group(models.Model):
    """Group class."""

    name = models.CharField(_('name'), max_length=80, unique=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('permissions'), blank=True,
        through='GroupPermission')

    objects = GroupManager()

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

    class Meta:
        """Meta Class."""

        app_label = app_label_name
        db_table = 'auth_group'
        default_related_name = 'goibibo_group'
        verbose_name = _('goibibo group')
        verbose_name_plural = _('goibibo groups')
        managed = False


class PermissionsMixin(models.Model):
    """Permission Mixin.
    A mixin class that adds the fields and methods necessary to support
    Django's Group and Permission model using the ModelBackend.
    """

    is_superuser = models.BooleanField(
        _('superuser status'), default=False,
        help_text=_('Designates that this user has all permissions without '
                    'explicitly assigning them.'))
    groups = models.ManyToManyField(
        Group, verbose_name=_('groups'),
        blank=True, help_text=_('The groups this user belongs to. A user will '
                                'get all permissions granted to each of '
                                'his/her group.'),
        related_name="user_set", related_query_name="user",
        through='UserGroup'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'), blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="user_set", related_query_name="user",
        through='UserPermission'
    )

    class Meta:
        """Meta Class."""

        app_label = app_label_name
        managed = False
        abstract = True

    def get_group_permissions(self, obj=None):
        """Get group permissions.
        Returns a list of permission strings that this user has through their
        groups. This method queries all available auth backends. If an object
        is passed in, only permissions matching this object are returned.
        """
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_group_permissions"):
                permissions.update(backend.get_group_permissions(self, obj))
        return permissions

    def get_all_permissions(self, obj=None):
        """Get all Permissions."""
        return _user_get_all_permissions(self, obj)

    def has_perm(self, perm, obj=None):
        """Check object has permission.
        Returns True if the user has the specified permission. This method
        queries all available auth backends, but returns immediately if any
        backend returns True. Thus, a user who has permission from a single
        auth backend is assumed to have permission in general. If an object is
        provided, permissions for this specific object are checked.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return _user_has_perm(self, perm, obj)

    def has_perms(self, perm_list, obj=None):
        """Check perm_list on object.
        Returns True if the user has each of the specified permissions. If
        object is passed, it checks if the user has all required perms for this
        object.
        """
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, app_label):
        """Check module permissions.
        Returns True if the user has any permissions in the given app label.
        Uses pretty much the same logic as has_perm, above.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        return _user_has_module_perms(self, app_label)


class AbstractUser(AbstractBaseUser, PermissionsMixin):
    """Abstract User class.
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.
    Username, password and email are required. Other fields are optional.
    """

    username = models.CharField(
        _('username'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, digits and '
                    '@/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(r'^[\w.@+-]+$', _('Enter a valid username.'), 'invalid')
        ])
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(
        _('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(
        _('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        app_label = app_label_name
        managed = False
        abstract = True

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this User."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class User(AbstractUser):
    """Goibibo database user model."""

    objects = UserManager()

    class Meta:   # nopep257
        app_label = app_label_name
        db_table = 'auth_user'
        default_related_name = 'goibibo_user'
        managed = False


class GroupPermission(models.Model):
    """Group permission inter-relation."""

    group = models.ForeignKey(Group, db_index=True, on_delete=models.CASCADE,
                              related_name='group_permission+')
    permission = models.ForeignKey(Permission, db_index=True, on_delete=models.CASCADE,
                                   related_name='group_permission+')

    class Meta:  # nopep257
        app_label = app_label_name
        db_table = 'auth_group_permissions'
        default_related_name = 'goibibo_group_permissions'
        managed = False


class UserGroup(models.Model):
    """User Group inter-relation."""

    user = models.ForeignKey(User, db_index=True, on_delete=models.CASCADE,
                             related_name='user_group+')
    group = models.ForeignKey(Group, db_index=True, on_delete=models.CASCADE,
                              related_name='user_group+')

    class Meta:
        """Meta Class."""

        app_label = app_label_name
        db_table = 'auth_user_groups'
        default_related_name = 'goibibo_user_groups'
        managed = False


class UserPermission(models.Model):
    """User permission inter-relation."""

    user = models.ForeignKey(User, db_index=True, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, db_index=True, on_delete=models.CASCADE,
                                   related_name='user_permission+')

    class Meta:
        """Meta Class."""

        app_label = app_label_name
        db_table = 'auth_user_user_permissions'
        default_related_name = 'goibibo_user_permissions'
        managed = False


class CustomUserProfile(models.Model):
    """Custom UserProfile."""

    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, related_name='userprofile')
    name = models.CharField(max_length=200, null=False, blank=True)
    password = models.CharField(max_length=200, null=False, blank=True)
    usertitle = models.CharField(max_length=10, null=False)
    firstname = models.CharField(max_length=50, null=False)
    middlename = models.CharField(max_length=50, null=True, blank=True)
    lastname = models.CharField(max_length=50, null=False)
    dob = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=30, null=False, blank=True)
    state = models.CharField(max_length=30, null=True, blank=True)
    pincode = models.IntegerField(null=True, blank=True)
    email = models.EmailField(null=False, max_length=60)
    mobile = models.CharField(max_length=10, null=True)
    salesrep = models.CharField(max_length=50, null=True, blank=True)
    fax = models.IntegerField(null=True, blank=True)
    pancard = models.CharField(max_length=30, null=True)
    agent = models.BooleanField(default=False)
    guid = models.CharField(max_length=50, null=True)
    email_unique = models.CharField(max_length=50, null=True, db_index=True)
    email_verified = models.BooleanField(default=False)
    mobile_verified = models.BooleanField(default=False)
    image_url = models.CharField(max_length=200, blank=True)
    credits_id = models.IntegerField(null=True, blank=True)
    link_user = models.ForeignKey(User, related_name="Main linked account id+",
                                  db_index=True, on_delete=models.DO_NOTHING)
    mobile_link_user_id = models.IntegerField(null=False, default=0)
    geocoordinate = models.CharField(max_length=50, null=True)
    optin_status = models.BooleanField(default=True, null=False)

    class Meta:
        """Meta class."""

        app_label = app_label_name
        db_table = profile_model_utils_obj.get_table_name("UserProfile")