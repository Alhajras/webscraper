from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Crawler, Template, Inspector, Runner, Indexer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "is_staff"]


class IndexerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indexer
        fields = "__all__"


class CrawlerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crawler
        fields = [
            "id",
            "name",
            "seed_url",
            "description",
            "created_at",
            "completed_at",
            "deleted",
            "template",
            "threads",
            "retry",
            "sleep",
            "timeout",
            "max_pages",
            "max_depth",
            "robot_file_url",
            "excluded_urls",
        ]


class InspectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspector
        fields = "__all__"


class RunnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Runner
        fields = [
            "id",
            "description",
            "created_at",
            "completed_at",
            "deleted",
            "crawler",
            "status",
            "collected_documents",
        ]


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = "__all__"

    inspectors = InspectorSerializer(many=True, read_only=True)
