from django.contrib import admin
from .models import Category, Question


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parent']
    list_filter = ['parent']
    search_fields = ['name']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'creator', 'difficulty', 'is_approved', 'created_at']
    list_filter = ['category', 'difficulty', 'is_approved', 'created_at']
    search_fields = ['title', 'answer']
    date_hierarchy = 'created_at'
