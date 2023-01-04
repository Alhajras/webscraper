from django.forms import ModelForm

from . import models


class SpiderForm(ModelForm):
    class Meta:
        model = models.Spider
        fields = ["name", "url", "description"]
