# -*- coding: utf-8 -*-
"""Sample API Methods."""
import coreapi
import coreschema
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, serializers, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.schemas import AutoSchema

from apps.apis.core.meta_data import MinimalMetadata
from apps.apis.core.proto import ProtoAPIView, ProtoRenderer
from apps.apis.core.sample_api.sampleproto_pb2 import SampleProto, Message


# -------x resources.py x--------


class SampleClass(object):
    """Sample Class for Sample API."""

    def __init__(self, first_name, last_name, email):
        """Initialize SampleClass instance."""
        self.first_name = first_name
        self.last_name = last_name
        self.email = email


# -------x serializers.py x--------

class SampleSerializer(serializers.Serializer):
    """Sample Serializer Class."""

    # pylint: disable=abstract-method
    first_name = serializers.CharField(required=True, max_length=100)
    last_name = serializers.CharField(required=True, max_length=100)
    email = serializers.EmailField(required=False, max_length=100)

    def create(self, validated_data):
        """Create new instance of sampleclass."""
        return SampleClass(**validated_data)


# -------x views.py x--------

@api_view(['GET'])
def api_root(request, format=None):
    """Return root data for sample_api."""
    # pylint: disable=redefined-builtin
    return Response({
        'hello': reverse('sample-hello', request=request, format=format),
        'list': reverse('sample-list', request=request, format=format),
        'hello2': reverse('sample2-hello', request=request, format=format),
        'list2': reverse('sample2-list', request=request, format=format),
    })


@api_view(['GET', 'POST'])
def hello_world(request):
    """Funtion hello world."""
    if request.method == 'POST':
        return Response({"message": "Hello world!", "data": request.data})
    return Response({"message": "Hello, world!"})


@csrf_exempt
@api_view(['GET', 'POST'])
def sample_list(request):
    """Return Simple list of first_name and last_name and email."""
    if request.method == 'POST':
        # data = JSONParser().parse(request)
        serializer = SampleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            resp = Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            resp = Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
    else:
        my_data = [SampleClass('Hare', 'Pathak', 'hare.pathak@go-mmt.com'),
                   SampleClass('Ashutosh', 'kumar', 'ashutosh.kumar@go-mmt.com')]
        results = SampleSerializer(my_data, many=True)
        resp = Response(results.data)
    return resp


class SampleViewSet(viewsets.GenericViewSet, ProtoAPIView):
    """Sample API Viewset."""

    # pylint: disable=too-many-ancestors
    queryset = []
    proto_model = SampleProto
    serializer_class = SampleSerializer
    renderer_classes = (JSONRenderer, ProtoRenderer)
    metadata_class = MinimalMetadata
    schema = AutoSchema(manual_fields=[
        coreapi.Field(
            "first_name",
            required=True,
            location="form",
            schema=coreschema.String(description="first name")
        ),
        coreapi.Field(
            "last_name",
            required=True,
            location="form",
            schema=coreschema.String(description="last name")
        ),
    ])

    def get_view_name(self):
        """Get view name(Example)."""
        return "Example APIs for depot"

    def get_view_description(self, html=False):
        """Get description(Example)."""
        return "These are the sample or example apis."

    @action(detail=False, methods=['GET', 'POST'], url_path='hello', url_name="hello")
    def hello_world(self, request):
        """Return Hello world."""
        self.proto_model = Message
        if request.method == 'POST':
            return Response({"message": "Hello world!", "data": request.data})
        return Response({"message": "Hello, world!"})

    @action(detail=False, methods=['GET', 'POST'], url_path='list', url_name="list")
    def sample_list(self, request):
        """Return and Create Sample List."""
        self.proto_model = SampleProto
        if request.method == 'POST':
            # data = JSONParser().parse(request)
            serializer = SampleSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                resp = Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                resp = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            my_data = [
                SampleClass('Hare', 'Pathak', 'hare.pathak@go-mmt.com'),
                SampleClass('Ashutosh', 'Kumar', 'ashutosh.kumar@go-mmt.com')
            ]
            results = SampleSerializer(my_data, many=True)
            resp = Response(results.data)
        return resp
