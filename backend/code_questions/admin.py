from django.contrib import admin
from .models import CodeQuestion, TestCase, CodeSubmission, CodeBookmark, CodeNote


@admin.register(CodeQuestion)
class CodeQuestionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'question_title', 'language', 'difficulty',
        'time_limit', 'memory_limit', 'is_public', 'created_at'
    ]
    list_filter = ['language', 'is_public', 'created_at']
    search_fields = ['question__title', 'question__explanation']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def question_title(self, obj):
        return obj.question.title
    question_title.short_description = '题目标题'

    def difficulty(self, obj):
        return obj.question.difficulty
    difficulty.short_description = '难度'


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'code_question', 'is_sample', 'is_hidden', 'order', 'created_at'
    ]
    list_filter = ['is_sample', 'is_hidden', 'created_at']
    search_fields = ['code_question__question__title']
    readonly_fields = ['created_at']
    ordering = ['code_question', 'order', 'id']


@admin.register(CodeSubmission)
class CodeSubmissionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'username', 'question_title', 'language',
        'status', 'runtime', 'passed_test_cases', 'total_test_cases', 'created_at'
    ]
    list_filter = ['status', 'language', 'created_at']
    search_fields = ['user__username', 'code_question__question__title']
    readonly_fields = [
        'created_at', 'status', 'runtime', 'memory',
        'passed_test_cases', 'total_test_cases', 'test_case_results'
    ]
    ordering = ['-created_at']

    def username(self, obj):
        return obj.user.username
    username.short_description = '用户'

    def question_title(self, obj):
        return obj.code_question.question.title
    question_title.short_description = '题目'


@admin.register(CodeBookmark)
class CodeBookmarkAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'question_title', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'code_question__question__title']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

    def username(self, obj):
        return obj.user.username
    username.short_description = '用户'

    def question_title(self, obj):
        return obj.code_question.question.title
    question_title.short_description = '题目'


@admin.register(CodeNote)
class CodeNoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'question_title', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'code_question__question__title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def username(self, obj):
        return obj.user.username
    username.short_description = '用户'

    def question_title(self, obj):
        return obj.code_question.question.title
    question_title.short_description = '题目'

    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = '内容预览'
