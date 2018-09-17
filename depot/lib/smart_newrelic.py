""" Smart Newrelic is to be used to create function based on newrelic python agent apis.
NewRelic Reserve Words::
    ago, and, as, auto, begin, begintime, compare, day, days, end, endtime, explain, facet,
    from, hour, hours, in, is, like, limit, minute, minutes, month, months, not, null, offset,
    or, second, seconds, select, since, timeseries, until, week, weeks, where, with
"""

import newrelic.agent


def get_current_transaction():
    """
    returns current newrelic transaction with all parameters.
    Returns:

    """
    transaction = newrelic.agent.current_transaction(active_only=True)

    return transaction


def add_custom_transaction_parameter(key, value):
    """

    Args:
        key(string): param_name     # Only the first 255 characters are retained.
        value: param_value  # Only the first 255 characters are retained.
        (string, integer, float, boolean)
    Returns:

    """
    success = newrelic.agent.add_custom_parameter(key, value)
    return success


def get_custom_param_value_from_transaction(key, transaction=None):
    """
    This function can be used to fetch pushed NR data from a transaction.
    Args:
        key: params_name  # Only the first 255 characters are retained.
        transation: given transaction to fetch data.

    Returns:

    """
    if not transaction:
        transaction = get_current_transaction()
    value = None
    if transaction:
        value = getattr(transaction, key)

    return value


def push_custom_parameters_transaction(custom_data):
    """
    this function can be used to push custom data as dict to newrelic.
    Args:
        custom_data(dict): event_data

    """
    for key, value in custom_data.items():
        add_custom_transaction_parameter(key, value)


def capture_request_params():
    """
    This call enables the capture of a web transaction's query string parameters as attributes.
    High security mode overrides this call if it is active,


    """
    newrelic.agent.capture_request_params()


def record_custom_metric(metric_category, metric_label, value):
    """
        This call records a single custom metric.
    Args:
        metric_category: to be used to create custom_name for metric
        metric_label: to be used for custom_name for metric
        value: value to be measured.
        (int, float or dict)

    Notes:
        name(string): format to be followed Custom/`Category`/`Label`
        The possible fields for a dictionary are:
            count: The number of things being measured. (Required)
            value/total: The total value measured across all things being counted. (Required)
            min/max: The minimum and maximum values when the count is > 1 (optional)
            sum_of_squares: It is used to calculate a standard deviation for a selection of data.


    Returns:

    """
    name = "Custom/{}/{}".format(metric_category, metric_label)
    newrelic.agent.record_custom_metric(name, value)


def record_custom_metrics(metrics):
    """
    This call records a set of custom metrics. The metrics is an iterable.
    The iterable can be a list, tuple or other iterable object, including a generator function.
    Args:
        metrics: any iterable object that yields (name, value) tuples.


    """
    newrelic.agent.record_custom_metrics(metrics)


def push_transaction_exception(post_data=None, capture_req_params=False):
    """
     This function is to be used to record any Python exception as an error,
    Args:
        post_data:

    Notes:
        We can record up to five distinct exceptions per transaction.

    """
    if not post_data:
        post_data = {}

    newrelic.agent.record_exception(params=post_data)
    if capture_req_params:
        capture_request_params()


def push_data_to_insights(event_type, params):
    """
    This records a custom event that can be viewed and queried in Insights.
    Args:
        event_type(string): defines the name (or type) of the custom event,
        params(dict):  Attaches custom attributes to the event.

    Returns:None
    Notes:
        There are limits and restrictions, please go through the below resource to know more.
        https://docs.newrelic.com/docs/agents/python-agent/python-agent-api/record_custom_event

    """
    newrelic.agent.record_custom_event(event_type, params)
