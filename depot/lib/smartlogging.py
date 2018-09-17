"""
This is custom logging framework for depot. This is wrapper class Python's
native logging API.
config is also updated to use this custom logging.

To use, simply 'from lib import smartlogging'.
"""
import logging
import logging.config


class DepotLogManager(logging.Manager):
    def __init__(self, rootnode):
        super().__init__(rootnode)
        self.loggerClass = DepotLogger


class DepotLogger(logging.Logger):
    """
    This is a custom logging framework for `depot`. This is a wrapper class around Python's
    native logging API. We can add additional parameters on specified logging messages.
    """
    def __init__(self, name, level=logging.NOTSET, log_type=""):
        super().__init__(name, level=level)
        self.log_type = log_type

    def __repr__(self):
        level = logging.getLevelName(self.getEffectiveLevel())
        return '<%s %s (%s)>' % (self.__class__.__name__, self.name, level)

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False,
             bucket="", stage="", log_type="", identifier="", extra_message="",
             track_id='', csid='', paymentid='', bookingid=''):
        """

        Args:
            level:
            msg: A string for developer message. It's mandatory and can
                     be supplied as the first argument or a keyword
                     argument.
            args:
            exc_info:
            extra:
            stack_info:
            bucket: A string for log bucket. It's mandatory if you want
                    your logs to be grouped properly.
            stage:
            track_id: tracker_id defined by client
            csid : client sessionid
            paymentid: paymentid of the booking.
            bookingid: booking id of the booking.

        Returns:

        """
        try:
            log_message = self._format_log_message(
                message=msg, bucket=bucket, stage=stage, track_id=track_id, csid=csid,
                paymentid=paymentid, bookingid=bookingid)
        except Exception as ex:
            log_message = msg + str(ex)
            exc_info = True
            stack_info = True

        super()._log(level, log_message, args, exc_info=exc_info, extra=extra,
                     stack_info=stack_info)

    @staticmethod
    def _safe_encode(item):
        """
        Safely encode to ASCII string.

        Args:
            item: Any object, string, unicode.

        Returns:
            An ASCII string representation for item.
        """
        if isinstance(item, str):
            if isinstance(item, bytes):
                item = item.decode('utf-8', 'replace')
        else:
            item = str(item)
        return item

    def _format_log_message(self, message="", bucket="", stage="", track_id='', csid='',
                            paymentid='', bookingid=''):
        """
        Generates log message.

        Returns '\\t\\x01' separated log message.
        """
        bucket = bucket or "UNKNOWN"
        stage = stage or "GENERAL"
        separator = '\t\x01'
        tracker_id = "_".join([x for x in [track_id, csid, paymentid, bookingid] if x])
        log_message = separator.join(
            [self._safe_encode(bucket),
             self._safe_encode(stage),
             self._safe_encode(tracker_id),
             self._safe_encode(message)]
        )
        return log_message


root = logging.RootLogger(logging.DEBUG)
DepotLogger.root = root
DepotLogger.manager = DepotLogManager(DepotLogger.root)


def getLogger(name=None):
    """
    Return a logger with the specified name, creating it if necessary.

    If no name is specified, return the root logger.
    """
    if name:
        logger = DepotLogger.manager.getLogger(name)
    else:
        logger = root
    return logger


class DepotDictConfigurator(logging.config.DictConfigurator):
    def configure_logger(self, name, config, incremental=False):
        """Configure a non-root logger from a dictionary."""
        logger = getLogger(name)
        self.common_logger_config(logger, config, incremental)
        propagate = config.get('propagate', None)
        if propagate is not None:
            logger.propagate = propagate


dictConfigClass = DepotDictConfigurator


def dictConfig(config):
    """Configure logging using a dictionary."""
    dictConfigClass(config).configure()
