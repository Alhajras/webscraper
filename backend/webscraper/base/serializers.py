from django.contrib.auth.models import User
from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from .models import (
    Crawler,
    Template,
    Inspector,
    Runner,
    Indexer,
    InspectorValue,
    ClickAction,
    ScrollAction,
    WaitAction,
    Statistics,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "is_staff"]


class CrawlerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crawler
        fields = [
            "id",
            "name",
            "seed_url",
            "description",
            "created_at",
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
            "scope_divs",
            "max_collected_docs",
            "show_browser",
            "parsing_algorithm",
            "allow_multi_elements",
        ]


class StatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistics
        fields = [
            "visited_pages",
            "average_docs_per_page",
            "average_processing_time",
            "avg_loading_time",
            "avg_page_size",
            "http_codes",
        ]


class InspectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspector
        fields = [
            "id",
            "name",
            "selector",
            "attribute",
            "type",
            "created_at",
            "deleted",
            "template",
            "template_name",
            "variable_name",
            "clean_up_expression",
            "indexer",
        ]


class IndexerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indexer
        fields = [
            "id",
            "name",
            "description",
            "status",
            "created_at",
            "completed_at",
            "b_parameter",
            "k_parameter",
            "q_gram_use_synonym",
            "q_gram_q",
            "dictionary",
            "skip_words",
            "weight_words",
            "small_words_threshold",
            "deleted",
            "inspectors_to_be_indexed",
            "boosting_formula",
            "inspectors",
        ]

    inspectors = InspectorSerializer(many=True, read_only=True)


class InspectorValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectorValue
        fields = [
            "id",
            "value",
            "url",
            "type",
            "attribute",
            "created_at",
            "deleted",
            "inspector",
            "runner",
            "document",
        ]


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
            "current_crawled_url",
            "name",
            "machine",
            "crawler_name",
            "statistics",
        ]

    statistics = StatisticsSerializer(read_only=True)


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = [
            "id",
            "name",
            "created_at",
            "deleted",
            "inspectors",
            "action_chain",
            "action_chain_disabled",
        ]

    inspectors = InspectorSerializer(many=True, read_only=True)


class ClickActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClickAction
        fields = "__all__"


class ScrollActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrollAction
        fields = "__all__"


class WaitActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitAction
        fields = "__all__"


class ActionPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        ScrollAction: ScrollActionSerializer,
        WaitAction: WaitActionSerializer,
        ClickAction: ClickActionSerializer,
    }
