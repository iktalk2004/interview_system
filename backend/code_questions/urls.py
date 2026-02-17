from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CodeQuestionViewSet, TestCaseViewSet, CodeSubmissionViewSet

router = DefaultRouter()
router.register(r'questions', CodeQuestionViewSet, basename='code-question')
router.register(r'test-cases', TestCaseViewSet, basename='test-case')
router.register(r'submissions', CodeSubmissionViewSet, basename='code-submission')

urlpatterns = [
    path('', include(router.urls)),
]
