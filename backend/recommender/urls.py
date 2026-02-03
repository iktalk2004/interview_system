from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserSimilarityViewSet,
    QuestionSimilarityViewSet,
    RecommendationViewSet,
    UserPreferenceViewSet,
    RecommendationSystemViewSet
)

router = DefaultRouter()
router.register(r'user-similarities', UserSimilarityViewSet, basename='user-similarities')
router.register(r'question-similarities', QuestionSimilarityViewSet, basename='question-similarities')
router.register(r'recommendations', RecommendationViewSet, basename='recommendations')
router.register(r'user-preferences', UserPreferenceViewSet, basename='user-preferences')
router.register(r'system', RecommendationSystemViewSet, basename='recommendation-system')

urlpatterns = [
    path('', include(router.urls)),
]
