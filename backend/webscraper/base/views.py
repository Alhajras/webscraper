from django.contrib.auth.models import User
from rest_framework import viewsets
from .models import Spider
from .serializers import SpiderSerializer, UserSerializer


class SpiderViewSet(viewsets.ModelViewSet):
    queryset = Spider.objects.all()
    serializer_class = SpiderSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
