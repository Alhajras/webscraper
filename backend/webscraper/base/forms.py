from django.forms import ModelForm

from . import models


class CrawlerForm(ModelForm):
    class Meta:
        model = models.Crawler
        fields = ["name", "seed_url", "description"]
