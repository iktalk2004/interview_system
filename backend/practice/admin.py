from django.contrib import admin
from .models import Interaction


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'question', 'status', 'score', 'time_spent', 'is_submitted', 'is_favorite',
                    'created_at']
    list_filter = ['status', 'is_submitted', 'is_favorite', 'created_at', 'score']
    search_fields = ['user__username', 'question__title']
    date_hierarchy = 'created_at'
