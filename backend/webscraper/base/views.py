from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins

from .filters import InspectorFilter
from .models import Spider, Template, Inspector
from .serializers import (
    SpiderSerializer,
    UserSerializer,
    TemplateSerializer,
    InspectorSerializer,
)


class EverythingButDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    pass


class SpiderViewSet(EverythingButDestroyViewSet):
    queryset = Spider.objects.filter(deleted=False)
    serializer_class = SpiderSerializer


class TemplateViewSet(EverythingButDestroyViewSet):
    queryset = Template.objects.filter(deleted=False)
    serializer_class = TemplateSerializer


class InspectorViewSet(EverythingButDestroyViewSet):
    queryset = Inspector.objects.filter(deleted=False)
    serializer_class = InspectorSerializer
    filterset_class = InspectorFilter
    filter_backends = [DjangoFilterBackend]
    filterset_fields = "template"


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
