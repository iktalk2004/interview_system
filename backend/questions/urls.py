from django.urls import path
from .views import CategoryViewSet, QuestionViewSet

urlpatterns = [
    path('categories/', CategoryViewSet.as_view(), name='categories'),
    path('questions/', QuestionViewSet.as_view(), name='questions'),
]
