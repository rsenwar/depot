"""Custom Metadata Classes."""

from rest_framework.metadata import BaseMetadata


class MinimalMetadata(BaseMetadata):
    """Minimal Metadata Class.

    Don't include field and other information for `OPTIONS` requests.
    Just return the name and description.

    """

    def determine_metadata(self, request, view):
        """Determine metadata. only `name` and `description`."""
        return {
            'name': view.get_view_name(),
            'description': view.get_view_description()
        }
