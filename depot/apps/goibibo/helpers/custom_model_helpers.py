"""Goibibo custom models helper."""
from apps.goibibo.models import User


def get_custom_user(username):
    """Fetch User object from custom_user model with username."""
    user = None
    user_obj_list = User.objects.filter(username=username)
    if user_obj_list:
        user = user_obj_list[0]  # pylint: disable=unsubscriptable-object
    return user


def get_custom_user_id(username):
    """Fetch user_id from custom_usr model with username.

    Args:
        username:

    Returns:
        (int)

    """
    u_id = 0
    user = get_custom_user(username)
    if user is not None:
        u_id = user.id      # pylint: disable=unsubscriptable-object
    return u_id


def get_custom_users(username_list):
    """Fetch user_id from custom_user model with username."""
    users = dict()
    user_obj_list = User.objects.filter(username__in=username_list)
    if user_obj_list:
        users = {a.username: a for a in user_obj_list}  # pylint: disable=not-an-iterable
    return users


def get_custom_user_ids(username_list):
    """Fetch user_id from custom_usr model with username.

    Args:
        username_list:

    Returns:
        (dict)

    """
    user_ids = dict()
    users = get_custom_users(username_list)
    if users:
        user_ids = {key: value.id for key, value in users.items()}

    return user_ids
