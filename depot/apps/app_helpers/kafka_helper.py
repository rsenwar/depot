"""Kafka Helper API."""
import logging
from threading import Lock

from django.conf import settings
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError, KafkaTimeoutError

from lib import smartjson


logger = logging.getLogger(__name__)


def on_send_success(record_metadata):
    """Log success data."""
    logger.info("%s\t%s\t%s\t%s\t%s", "KafkaPush", "success", record_metadata.topic,
                record_metadata.partition, record_metadata.offset)


def on_send_error(excp):
    """Log Error Data."""
    logger.error("%s\t%s", "KafkaPush", "error", exc_info=excp)
    # handle exception


def make_data_safe(raw_data):
    """Make data safe."""
    if isinstance(raw_data, dict) is True:
        raw_data = smartjson.dumps(raw_data)
    if not isinstance(raw_data, bytes):
        data = raw_data.encode(encoding='utf-8', errors='ignore')
    else:
        data = raw_data

    return data


class KafkaHelper(object):
    """Kafka Helper Class.

    This class will be used to create Kafka connection object as per configs.

    """

    _producer = None

    @staticmethod
    def get_kafka_producer(key_serializer=None, value_serializer=None):
        """Get kafka producer."""
        new_connection = False
        is_new_ks = (key_serializer is not None and hash(key_serializer) != hash(make_data_safe))
        is_new_vs = (value_serializer is not None and
                     hash(value_serializer) != hash(make_data_safe))
        if is_new_ks or is_new_vs:
            new_connection = True
        value_serializer = make_data_safe if value_serializer is None else value_serializer
        key_serializer = make_data_safe if key_serializer is None else key_serializer
        if new_connection:
            kafka_conn = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BROKERS,
                value_serializer=value_serializer,
                key_serializer=key_serializer,
                retries=3)
        else:
            kafka_conn = KafkaHelper._producer
            if kafka_conn:
                try:
                    # pylint: disable=protected-access
                    if kafka_conn._closed or \
                            kafka_conn._sender._client._closed or \
                            kafka_conn._accumulator._closed:
                        kafka_conn = None
                except Exception:
                    kafka_conn = None

            if kafka_conn is None:
                with Lock():
                    if kafka_conn is None:
                        kafka_conn = KafkaProducer(
                            bootstrap_servers=settings.KAFKA_BROKERS,
                            value_serializer=make_data_safe,
                            retries=3)
            KafkaHelper._producer = kafka_conn

        return kafka_conn


def push_to_kafka_asynchronous(topic_name, data, key=None, key_serializer=None,
                               value_serializer=None):
    """Push data to kafka asynchronous way."""
    resp = 'async'
    try:
        if key_serializer is not None or value_serializer is not None:
            producer = KafkaHelper.get_kafka_producer(key_serializer=key_serializer,
                                                      value_serializer=value_serializer)
        else:
            producer = KafkaHelper.get_kafka_producer()
        if not producer._closed:    # pylint: disable=protected-access
            producer.send(topic_name, value=data, key=key) \
                .add_callback(on_send_success) \
                .add_errback(on_send_error)
        else:
            resp = 'failed'

    except KafkaTimeoutError as kter:
        logger.critical("KafkaPush timeout err: %s, topic: %s, data: %s", kter, topic_name,
                        data)
    except KafkaError as ker:
        logger.critical("KafkaPush kafka err: %s, topic: %s, data: %s", ker, topic_name, data)
    except Exception as ex:
        logger.critical("KafkaPush Exception err: %s, topic: %s, data: %s", ex, topic_name,
                        data)

    return resp


def push_to_kafka_synchronous(topic_name, data, key=None, key_serializer=None,
                              value_serializer=None):
    """Push data to Kafka synchronous."""
    resp = 'failed'
    try:
        if key_serializer is not None or value_serializer is not None:
            producer = KafkaHelper.get_kafka_producer(key_serializer=key_serializer,
                                                      value_serializer=value_serializer)
        else:
            producer = KafkaHelper.get_kafka_producer()
        resp = producer.send(topic_name, value=data, key=key) \
            .add_callback(on_send_success) \
            .add_errback(on_send_error).get(timeout=1)

        if resp is not None and resp != 'failed':
            resp = 'successful'

    except KafkaTimeoutError as kter:
        logger.critical("KafkaPush timeout err: %s, topic: %s, data: %s", kter, topic_name,
                        data)
    except KafkaError as ker:
        logger.critical("KafkaPush kafka err: %s, topic: %s, data: %s", ker, topic_name, data)
    except Exception as ex:
        logger.critical("KafkaPush Exception err: %s, topic: %s, data: %s", ex, topic_name,
                        data)

    return resp


def get_group_kafka_consumer(topic_name, group_id=None, auto_offset_reset='earliest'):
    """Get Kafka Consumer."""
    if group_id:
        consumer = KafkaConsumer(topic_name, group_id=group_id,
                                 bootstrap_servers=settings.KAFKA_BROKERS,
                                 auto_offset_reset=auto_offset_reset)
    else:
        consumer = KafkaConsumer(topic_name,
                                 bootstrap_servers=settings.KAFKA_BROKERS,
                                 auto_offset_reset=auto_offset_reset)
    return consumer


def read_message_from_consumer(consumer):
    """Read messages from consumers."""
    for msg in consumer:
        print(msg.value)
        print("%s:%d:%d: key=%s value=%s" % (msg.topic, msg.partition,
                                             msg.offset, msg.key,
                                             msg.value))
