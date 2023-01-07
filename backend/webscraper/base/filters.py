import django_filters
from .models import Inspector


class InspectorFilter(django_filters.FilterSet):
    class Meta:
        model = Inspector
        fields = ["template"]

    template = django_filters.Filter(field_name="template", lookup_expr="exact")
