"""Model utils to add `app_name` and `table_name`."""


class ModelUtils(object):
    """class Model Utils which define app_name and table_name."""

    def __init__(self, table_prefix):
        """Initialize class modelutils."""
        self.__app_name = 'goibibo'
        self.__table_prefix = table_prefix

    def get_app_name(self):
        """Return app_name."""
        return self.__app_name

    def get_table_name(self, class_name):
        """Return table_name."""
        table_name = "%s_%s" % (self.__table_prefix, class_name)
        return table_name.lower()