from django.contrib import admin
from .models import UserSimilarity, QuestionSimilarity, Recommendation, UserPreference


@admin.register(UserSimilarity)
class UserSimilarityAdmin(admin.ModelAdmin):
    list_display = ['user_a', 'user_b', 'similarity_score', 'common_questions', 'last_updated']
    list_filter = ['last_updated']
    search_fields = ['user_a__username', 'user_b__username']
    ordering = ['-similarity_score']


@admin.register(QuestionSimilarity)
class QuestionSimilarityAdmin(admin.ModelAdmin):
    list_display = ['question_a', 'question_b', 'similarity_score', 'common_users', 'last_updated']
    list_filter = ['last_updated']
    search_fields = ['question_a__title', 'question_b__title']
    ordering = ['-similarity_score']


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'recommendation_type', 'score', 'is_viewed', 'is_answered', 'created_at']
    list_filter = ['recommendation_type', 'is_viewed', 'is_answered', 'created_at']
    search_fields = ['user__username', 'question__title']
    ordering = ['-score', '-created_at']
    readonly_fields = ['created_at']


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'avg_score', 'total_answered', 'last_updated']
    list_filter = ['last_updated']
    search_fields = ['user__username']
    readonly_fields = ['last_updated']
