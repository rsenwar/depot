"""Depot Project Views."""
import logging

from django.apps import apps
from django.http import HttpResponse

from django.apps import apps
from django.contrib.admin.views.decorators import user_passes_test
from django.contrib.auth.management import _get_all_permissions
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse, HttpResponse
from django.views import View
from apps.goibibo.models import CustomSite

logger = logging.getLogger('depot')


class IndexView(View):
    """Index Page for Depot project."""

    def get(self, request):
        """Return root function."""
        site_obj = get_current_site(request)
        goibibo_site_obj = CustomSite.objects.get(pk=2)
        logger.info("%s\t%s", "views", "welcome to depot",
                    extra=dict(bucket="check", stage="index"))

        resp_msg = {
            'msg': "Welcome to Bus Transaction Service!!",
            'name': site_obj.name,
            'goibibo_site_name': goibibo_site_obj.name
        }
        return JsonResponse(resp_msg)


@user_passes_test(lambda u: u.is_superuser)
def create_user(request):
    """Create user."""
    logger.info("%s\t%s", "create user", request.GET)
    if not request.GET:
        raise ValueError("No Input param given")
    uname = request.GET.get('un')
    email = request.GET.get('em')
    pswd = 'try again.'
    su = request.GET.get('su', '0')
    user = None
    if uname and email:
        if int(su):
            pswd = User.objects.make_random_password(10)
            user = User.objects.create_superuser(uname, email, pswd)
        else:
            pswd = User.objects.make_random_password(10)
            user = User.objects.create_user(uname, email, pswd)
            user.is_staff = True
            user.save()
    if user:
        msg = "User has been created with mentioned password %s."
    else:
        msg = "Some error occured. %s"
    return HttpResponse(msg % pswd)


@user_passes_test(lambda u: u.is_superuser)
def create_permissions_content_types(request):
    """Create permissions and content_type."""
    # pylint: disable=unpacking-non-sequence
    msg_list = []
    for model in apps.get_models():
        opts = model._meta
        logger.info("%s\t%s", "create permissions model name", opts.verbose_name_raw)
        ctype, created = ContentType.objects.get_or_create(
            app_label=opts.app_label,
            model=opts.object_name.lower())
        logger.info("%s\t%s\t%s", "Adding Content_type", ctype, created)
        if created:
            msg_list.append('Adding content_type {}'.format(ctype))
        for codename, name in _get_all_permissions(opts):
            p, created = Permission.objects.get_or_create(
                codename=codename,
                content_type=ctype,
                defaults={'name': name})
            logger.info("%s\t%s\t%s", "Adding permission", p, created)
            if created:
                msg_list.append('Adding permission {}'.format(p))

    msg = "\n".join(msg_list)
    if not msg:
        msg = 'No new permissions or contenttype added.'

    return HttpResponse(msg)