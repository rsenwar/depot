
from dict_to_proto3_to_dict.dict_to_proto3_to_dict import protobuf_to_dict
from django.conf import settings
from django.utils import six
from rest_framework.exceptions import ParseError
from rest_framework.parsers import BaseParser

MISSING_MODEL_ERROR = 'Model not specified for proto response'


class ProtoParser(BaseParser):
    media_type = 'application/octet-stream'
    format = 'proto'
    proto_model = None

    def post_parser(self, py_model):
        """
        any changes to py_model before sending to old code
        :param py_model:
        :return:
        """
        pass

    def parse(self, stream, media_type=None, parser_context=None):
        parser_context = parser_context or {}
        encoding = parser_context.get('encoding', settings.DEFAULT_CHARSET)
        cls = self.proto_model or parser_context.get('proto_model', None)
        if not cls:
            raise Exception(MISSING_MODEL_ERROR)
        try:
            data = stream.read().decode(encoding)
            pb_model = cls()
            pb_model.ParseFromString(data.encode())
            py_model = protobuf_to_dict(pb_model)
            self.post_parser(py_model)
            return py_model
        except Exception as e:
            raise ParseError('Protocolbuffer parse error - %s' % six.text_type(e))

