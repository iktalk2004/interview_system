from django.contrib import admin
from .models import UserStats, CategoryStats, DailyStats, PerformanceTrend


@admin.register(UserStats)
class UserStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_questions_answered', 'average_score', 'highest_score',
                    'lowest_score', 'total_time_spent', 'favorite_count', 'last_activity']
    list_filter = ['last_activity']
    search_fields = ['user__username']
    ordering = ['-total_questions_answered']
    readonly_fields = ['last_activity']


@admin.register(CategoryStats)
class CategoryStatsAdmin(admin.ModelAdmin):
    list_display = ['category', 'total_questions', 'total_answers', 'average_score',
                    'most_difficult', 'easiest', 'last_updated']
    list_filter = ['last_updated']
    search_fields = ['category__name']
    ordering = ['-total_answers']
    readonly_fields = ['last_updated']


@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = ['date', 'user', 'questions_answered', 'questions_viewed',
                    'average_score', 'time_spent']
    list_filter = ['date']
    search_fields = ['user__username']
    ordering = ['-date']


@admin.register(PerformanceTrend)
class PerformanceTrendAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'score_trend', 'accuracy_trend', 'speed_trend']
    list_filter = ['date']
    search_fields = ['user__username']
    ordering = ['-date']
