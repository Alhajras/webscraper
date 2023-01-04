from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("spider", views.create_spider, name="create spider"),
]
