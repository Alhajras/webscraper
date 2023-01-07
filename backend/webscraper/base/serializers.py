from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Spider, Template, Inspector


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "is_staff"]


class SpiderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spider
        fields = ["id", "name", "url", "description", "created_at", "completed_at", "status", "deleted"]


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ["__all__"]


class InspectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspector
        fields = ["__all__"]
