"""Logging helpers for crystal.

This is collection of logging helper functions and classes for crystal.

"""
import logging


def _safe_encode(item):
    """Safely encode to ASCII string.

    Args:
        item: Any object, string, unicode.

    Returns:
        An ASCII string representation for item.

    """
    if not isinstance(item, str):
        if isinstance(item, bytes):
            item = item.decode('utf-8', 'replace')
        else:
            item = str(item)
    return item


class DepotFormatter(logging.Formatter):
    """Crystal Log Formatter."""

    def formatMessage(self, record):
        """Format Message for logging.

        Args:
            record:

        """
        record.extra_msg = self._get_extra_message(record)
        return super().formatMessage(record)

    @staticmethod
    def _get_extra_message(record):
        """Get extra log message.

        Args:
            record: An instance of class LogRecord.

        Returns:
            (string) -  extra_msg to add in log message.

        """
        separator = '\t\x01'
        record_dict = record.__dict__
        bucket = record_dict.get('bucket', "UNKNOWN")
        stage = record_dict.get('stage', 'GENERAL')
        track_id = record_dict.get('track_id', '')
        csid = record_dict.get('csid', '')
        paymentid = record_dict.get('paymentid', '')
        bookingid = record_dict.get('bookingid', '')
        tracker_id = "_".join([x for x in [track_id, csid, paymentid, bookingid] if x])

        extra_msg = separator.join(
            [_safe_encode(bucket),
             _safe_encode(stage),
             _safe_encode(tracker_id)]
        )
        return extra_msg

    def formatException(self, ei):
        """Format Exception."""
        s = super().formatException(ei)
        s = s.replace("\n", "-->")
        return s
