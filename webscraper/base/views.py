from django.shortcuts import render
from . import models


def index(request):
    spiders = models.Spider.objects.filter(deleted=False)
    context = {"spiders": spiders}

    return render(request, "index.html", context)
