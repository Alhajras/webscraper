from django.shortcuts import render
from . import models
from .forms import SpiderForm


def index(request):
    spiders = models.Spider.objects.filter(deleted=False)
    context = {"spiders": spiders}

    return render(request, "index.html", context)


def create_spider(request):
    if request.method == "POST":
        form = SpiderForm(request.POST)
        if form.is_valid():
            models.Spider.objects.create(
                name=form.cleaned_data["name"],
                url=form.cleaned_data["url"],
                description=form.cleaned_data["description"],
            )
    spiders = models.Spider.objects.filter(deleted=False)
    context = {"spiders": spiders}
    return render(request, "index.html", context)
