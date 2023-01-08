from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"spiders", views.SpiderViewSet, "spiders")
router.register(r"templates", views.TemplateViewSet, "templates")
router.register(r"inspectors", views.InspectorViewSet, "inspectors")
router.register(r"runners", views.RunnerViewSet, "runners")

urlpatterns = [
    path("", include(router.urls)),
]
