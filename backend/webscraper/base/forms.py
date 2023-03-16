from django.forms import ModelForm

from . import models


class CrawlerForm(ModelForm):
    class Meta:
        model = models.Crawler
        fields = ["name", "url", "description"]
