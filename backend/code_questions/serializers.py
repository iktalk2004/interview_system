from rest_framework import serializers
from .models import CodeQuestion, TestCase, CodeSubmission, CodeBookmark, CodeNote
from questions.serializers import QuestionSerializer


class CodeQuestionSerializer(serializers.ModelSerializer):
    """
    代码题目序列化器
    """
    question = QuestionSerializer(read_only=True)
    question_id = serializers.IntegerField(write_only=True)
    language_display = serializers.CharField(source='get_language_display', read_only=True)

    class Meta:
        model = CodeQuestion
        fields = [
            'id', 'question', 'question_id', 'language', 'language_display',
            'template_code', 'starter_code', 'function_signature',
            'time_limit', 'memory_limit', 'is_public',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CodeQuestionListSerializer(serializers.ModelSerializer):
    """
    代码题目列表序列化器（简化版）
    """
    title = serializers.CharField(source='question.title')
    difficulty = serializers.IntegerField(source='question.difficulty')
    difficulty_display = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='question.category.name', allow_null=True)
    language_display = serializers.CharField(source='get_language_display', read_only=True)

    class Meta:
        model = CodeQuestion
        fields = [
            'id', 'title', 'difficulty', 'difficulty_display',
            'category_name', 'language', 'language_display',
            'time_limit', 'memory_limit', 'is_public'
        ]

    def get_difficulty_display(self, obj):
        difficulty_map = {1: 'Easy', 2: 'Medium', 3: 'Hard'}
        return difficulty_map.get(obj.question.difficulty, 'Unknown')


class TestCaseSerializer(serializers.ModelSerializer):
    """
    测试用例序列化器
    """
    class Meta:
        model = TestCase
        fields = [
            'id', 'code_question', 'input_data', 'expected_output',
            'is_hidden', 'is_sample', 'order', 'created_at'
        ]
        read_only_fields = ['created_at']


class CodeSubmissionSerializer(serializers.ModelSerializer):
    """
    代码提交序列化器
    """
    username = serializers.CharField(source='user.username', read_only=True)
    question_title = serializers.CharField(source='code_question.question.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    language_display = serializers.CharField(source='get_language_display', read_only=True)
    pass_rate = serializers.SerializerMethodField()

    class Meta:
        model = CodeSubmission
        fields = [
            'id', 'user', 'username', 'code_question', 'question_title',
            'code', 'language', 'language_display', 'status', 'status_display',
            'runtime', 'memory', 'passed_test_cases', 'total_test_cases',
            'pass_rate', 'error_message', 'test_case_results', 'created_at'
        ]
        read_only_fields = ['created_at', 'status', 'runtime', 'memory', 'passed_test_cases', 'total_test_cases']

    def get_pass_rate(self, obj):
        if obj.total_test_cases == 0:
            return 0
        return round((obj.passed_test_cases / obj.total_test_cases) * 100, 2)


class CodeSubmissionCreateSerializer(serializers.ModelSerializer):
    """
    代码提交创建序列化器
    """
    class Meta:
        model = CodeSubmission
        fields = ['code', 'language']


class CodeBookmarkSerializer(serializers.ModelSerializer):
    """
    代码题目收藏序列化器
    """
    username = serializers.CharField(source='user.username', read_only=True)
    question_title = serializers.CharField(source='code_question.question.title', read_only=True)

    class Meta:
        model = CodeBookmark
        fields = ['id', 'user', 'username', 'code_question', 'question_title', 'created_at']
        read_only_fields = ['created_at']


class CodeNoteSerializer(serializers.ModelSerializer):
    """
    代码题目笔记序列化器
    """
    username = serializers.CharField(source='user.username', read_only=True)
    question_title = serializers.CharField(source='code_question.question.title', read_only=True)

    class Meta:
        model = CodeNote
        fields = ['id', 'user', 'username', 'code_question', 'question_title', 'content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CodeQuestionDetailSerializer(CodeQuestionSerializer):
    """
    代码题目详情序列化器（包含测试用例）
    """
    sample_test_cases = serializers.SerializerMethodField()
    total_test_cases = serializers.SerializerMethodField()
    user_bookmarked = serializers.SerializerMethodField()
    user_note = serializers.SerializerMethodField()

    class Meta(CodeQuestionSerializer.Meta):
        fields = CodeQuestionSerializer.Meta.fields + [
            'sample_test_cases', 'total_test_cases', 'user_bookmarked', 'user_note'
        ]

    def get_sample_test_cases(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            test_cases = obj.test_cases.filter(is_sample=True, is_hidden=False)
        else:
            test_cases = obj.test_cases.filter(is_sample=True, is_hidden=False)
        return TestCaseSerializer(test_cases, many=True).data

    def get_total_test_cases(self, obj):
        return obj.test_cases.count()

    def get_user_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CodeBookmark.objects.filter(
                user=request.user,
                code_question=obj
            ).exists()
        return False

    def get_user_note(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                note = CodeNote.objects.get(
                    user=request.user,
                    code_question=obj
                )
                return CodeNoteSerializer(note).data
            except CodeNote.DoesNotExist:
                return None
        return None
