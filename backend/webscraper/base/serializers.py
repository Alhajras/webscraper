from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Spider


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "is_staff"]


class SpiderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spider
        fields = ["name", "url", "description", "created_at", "completed_at", "status"]