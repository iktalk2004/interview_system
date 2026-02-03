from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScoringViewSet

router = DefaultRouter()
router.register(r'scoring', ScoringViewSet, basename='scoring')

urlpatterns = [
    path('', include(router.urls)),
]
