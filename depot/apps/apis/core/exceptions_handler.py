"""Custom Exception handler for rest_framework APIs."""

from rest_framework.views import exception_handler


def exception_handler_proto(exc, context):
    """Exception handler for proto."""
    resp = exception_handler(exc, context)
    if resp is not None:
        pass

    return resp
