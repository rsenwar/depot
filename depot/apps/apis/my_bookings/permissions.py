"""My Booking permissions."""

from rest_framework.permissions import BasePermission


class MyBookingsPermission(BasePermission):
    """My Stays api permission."""

    def has_permission(self, request, view):
        """Allow the active user to fetch the my bookings data."""
        return True
        # return request.user and request.user.is_authenticated
