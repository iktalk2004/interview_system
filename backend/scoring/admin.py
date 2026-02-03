from django.contrib import admin
from .models import ScoringHistory


@admin.register(ScoringHistory)
class ScoringHistoryAdmin(admin.ModelAdmin):
    list_display = ['interaction', 'scoring_method', 'score', 'created_at']
    list_filter = ['scoring_method', 'created_at']
    search_fields = ['interaction__user__username', 'interaction__question__title']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
