"""Proto API View."""
from rest_framework.views import APIView, api_settings


class ProtoAPIView(APIView):
    """Proto APIView class."""

    proto_model = None
    use_proto_model_in_exc = False

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(**kwargs)
        self.exception = False
        self.type = 'str'

    def get_renderer_context(self):
        """Return a dict that is passed through to Renderer.render()."""
        renderer_context = super().get_renderer_context()
        renderer_context['proto_model'] = self.proto_model
        renderer_context['exception'] = self.exception
        renderer_context['type'] = self.type
        renderer_context['use_proto_model_in_exc'] = self.use_proto_model_in_exc
        return renderer_context

    def get_parser_context(self, http_request):
        """Return a dict that is passed through to Parser.parse()."""
        parser_context = super().get_parser_context(http_request)
        parser_context['proto_model'] = self.proto_model
        return parser_context

    def get_renderers(self):
        """Instantiate and return the list of renderers that this view can use.

        Add our preferred renderer to the start of the list. Populated from class level and
        method level `renderer_classes`

        Returns:
            A list of valid renderers. Which renderer will be selected will be
                 dependent on format requested.

        """
        renderers = list(list(self.renderer_classes) + api_settings.DEFAULT_RENDERER_CLASSES)
        return [renderer() for renderer in renderers]

    def get_parsers(self):
        """Instantiate and return the list of parsers that this view can use.

        Add our preferred parser to the start of the list. Populated from class level and
        method level `parser_classes`

        Returns:
            A list of valid parsers.

        """
        parsers = list(list(self.parser_classes) + api_settings.DEFAULT_PARSER_CLASSES)
        return [parser() for parser in parsers]

    def handle_exception(self, exc):
        """Handle any exception that occurs.

        Args:
            exc:

        Returns:
            On exception sets the type of exception.

        """
        response = super().handle_exception(exc)
        self.exception = response.exception
        if getattr(exc, 'detail', None) and isinstance(exc.detail, (list, dict)):
            # `detail field is not populated for 404 and 403 exceptions`
            self.type = 'dict'
        return response

    def get_exception_handler(self):
        """Return the exception handler that this view uses."""
        from apps.apis.core.exceptions_handler import exception_handler_proto
        return exception_handler_proto
