"""Proto response renderer.

Renderers are used to serialize a response into specific media types.

"""
from rest_framework.renderers import BaseRenderer

from dict_to_proto3_to_dict.dict_to_proto3_to_dict import dict_to_protobuf

from apps.apis.core.proto.exception_pb2 import Exception as ProtoException

MISSING_MODEL_ERROR = 'Model not specified for proto response'


class ProtoRenderer(BaseRenderer):
    """Renderer which serializes to proto-message."""

    media_type = 'application/octet-stream'
    format = 'proto'
    charset = 'utf-8'
    proto_model = None

    def pre_render(self, data):
        """Change to dict before sending to protobuf.

        Args:
            data:

        Returns:

        """
        pass

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """Render `data` into proto-message."""
        renderer_context = renderer_context or {}
        self.pre_render(data)
        resp = []
        use_proto_model = renderer_context.get('use_proto_model_in_exc', False)
        if renderer_context.get('exception', False) and not use_proto_model:
            resp = ProtoRenderer.protofy_error(data, renderer_context)
        else:
            if isinstance(data, list):
                for dat in data:
                    resp.append(self.protofy_item(dat, renderer_context))
            else:
                resp = self.protofy_item(data, renderer_context)
        return resp

    def protofy_item(self, data, renderer_context):
        """Protofy the item."""
        cls = self.proto_model or renderer_context.get('proto_model', None)
        if not cls:
            raise Exception(MISSING_MODEL_ERROR)
        pb_model = cls()
        dict_to_protobuf(data, pb_model)
        item = pb_model.SerializeToString()
        return item

    @staticmethod
    def protofy_error(data, renderer_context):
        """Protofy the error message.

        In case of 404, 403 status codes we load a custom model with success as default
        false and in `detail` field add the exception details. In case the exception detail
        itself is a dict(rest_framework/views.py:72) we cast it to string and go ahead.
        """
        pb_model = ProtoException()
        if renderer_context.get('type', 'str') == 'dict':
            data = {'detail': str(data, 'utf-8')}
        dict_to_protobuf(data, pb_model)
        resp = pb_model.SerializeToString()
        return resp
