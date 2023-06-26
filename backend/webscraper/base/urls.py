from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"crawlers", views.CrawlerViewSet, "spiders")
router.register(r"templates", views.TemplateViewSet, "templates")
router.register(r"inspectors", views.InspectorViewSet, "inspectors")
router.register(r"inspector-values", views.InspectorValueViewSet, "inspector-values")
router.register(r"runners", views.RunnerViewSet, "runners")
router.register(r"indexers", views.IndexerViewSet, "indexers")
router.register(r"actions", views.ActionViewSet, "actions")

urlpatterns = [
    path("", include(router.urls)),
]
