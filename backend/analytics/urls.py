from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserStatsViewSet,
    CategoryStatsViewSet,
    DailyStatsViewSet,
    PerformanceTrendViewSet,
    AnalyticsDashboardViewSet
)

router = DefaultRouter()
router.register(r'user-stats', UserStatsViewSet, basename='user-stats')
router.register(r'category-stats', CategoryStatsViewSet, basename='category-stats')
router.register(r'daily-stats', DailyStatsViewSet, basename='daily-stats')
router.register(r'performance-trends', PerformanceTrendViewSet, basename='performance-trends')
router.register(r'dashboard', AnalyticsDashboardViewSet, basename='analytics-dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
