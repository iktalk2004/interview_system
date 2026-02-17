from django.db import models
from questions.models import Question, Category
from users.models import User


class CodeQuestion(models.Model):
    """
    代码题目模型
    """
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('java', 'Java'),
        ('javascript', 'JavaScript'),
        ('cpp', 'C++'),
        ('go', 'Go'),
        ('rust', 'Rust'),
    ]

    question = models.OneToOneField(
        Question,
        on_delete=models.CASCADE,
        related_name='code_question'
    )
    language = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        default='python'
    )
    template_code = models.TextField(
        help_text='代码模板，用户在此基础上编写'
    )
    starter_code = models.TextField(
        blank=True,
        help_text='初始代码，自动填充到编辑器'
    )
    function_signature = models.CharField(
        max_length=200,
        help_text='函数签名，如 def solution(nums):'
    )
    time_limit = models.IntegerField(
        default=1000,
        help_text='时间限制（毫秒）'
    )
    memory_limit = models.IntegerField(
        default=256,
        help_text='内存限制（MB）'
    )
    is_public = models.BooleanField(
        default=True,
        help_text='是否公开'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'code_questions'
        verbose_name = '代码题目'
        verbose_name_plural = '代码题目'

    def __str__(self):
        return f"{self.question.title} ({self.language})"


class TestCase(models.Model):
    """
    测试用例模型
    """
    code_question = models.ForeignKey(
        CodeQuestion,
        on_delete=models.CASCADE,
        related_name='test_cases'
    )
    input_data = models.TextField(
        help_text='输入数据，JSON 格式'
    )
    expected_output = models.TextField(
        help_text='期望输出，JSON 格式'
    )
    is_hidden = models.BooleanField(
        default=False,
        help_text='是否隐藏（隐藏用例不显示给用户）'
    )
    is_sample = models.BooleanField(
        default=False,
        help_text='是否为示例用例'
    )
    order = models.IntegerField(
        default=0,
        help_text='排序'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'test_cases'
        verbose_name = '测试用例'
        verbose_name_plural = '测试用例'
        ordering = ['order', 'id']

    def __str__(self):
        return f"TestCase {self.id} for {self.code_question.question.title}"


class CodeSubmission(models.Model):
    """
    代码提交记录模型
    """
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('running', '运行中'),
        ('accepted', '通过'),
        ('wrong_answer', '答案错误'),
        ('time_limit_exceeded', '超时'),
        ('memory_limit_exceeded', '内存超限'),
        ('runtime_error', '运行时错误'),
        ('compile_error', '编译错误'),
        ('system_error', '系统错误'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='code_submissions'
    )
    code_question = models.ForeignKey(
        CodeQuestion,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    code = models.TextField(help_text='提交的代码')
    language = models.CharField(max_length=20)
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='pending'
    )
    runtime = models.IntegerField(
        null=True,
        blank=True,
        help_text='运行时间（毫秒）'
    )
    memory = models.IntegerField(
        null=True,
        blank=True,
        help_text='内存使用（KB）'
    )
    passed_test_cases = models.IntegerField(
        default=0,
        help_text='通过的测试用例数'
    )
    total_test_cases = models.IntegerField(
        default=0,
        help_text='总测试用例数'
    )
    error_message = models.TextField(
        blank=True,
        help_text='错误信息'
    )
    test_case_results = models.JSONField(
        default=dict,
        blank=True,
        help_text='测试用例结果详情'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'code_submissions'
        verbose_name = '代码提交'
        verbose_name_plural = '代码提交'
        ordering = ['-created_at']

    def __str__(self):
        return f"Submission {self.id} by {self.user.username}"


class CodeBookmark(models.Model):
    """
    代码题目收藏模型
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='code_bookmarks'
    )
    code_question = models.ForeignKey(
        CodeQuestion,
        on_delete=models.CASCADE,
        related_name='bookmarks'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'code_bookmarks'
        verbose_name = '代码题目收藏'
        verbose_name_plural = '代码题目收藏'
        unique_together = ['user', 'code_question']

    def __str__(self):
        return f"{self.user.username} bookmarked {self.code_question.question.title}"


class CodeNote(models.Model):
    """
    代码题目笔记模型
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='code_notes'
    )
    code_question = models.ForeignKey(
        CodeQuestion,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    content = models.TextField(help_text='笔记内容')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'code_notes'
        verbose_name = '代码题目笔记'
        verbose_name_plural = '代码题目笔记'

    def __str__(self):
        return f"Note by {self.user.username} for {self.code_question.question.title}"
