from django.db import models
from users.models import User
from questions.models import Question


class QuestionHistory(models.Model):
    """
    题目历史版本模型
    用于追踪题目的修改历史
    """
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='history'
    )
    version = models.IntegerField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    answer = models.TextField(blank=True)
    explanation = models.TextField(blank=True)
    difficulty = models.IntegerField()
    category = models.ForeignKey(
        'questions.Category',
        on_delete=models.SET_NULL,
        null=True
    )
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_question_versions'
    )
    change_reason = models.TextField(blank=True, help_text='修改原因')

    class Meta:
        verbose_name = '题目历史'
        verbose_name_plural = '题目历史'
        ordering = ['-version']
        indexes = [
            models.Index(fields=['question', 'version']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.question.title} v{self.version}"


class WrongQuestion(models.Model):
    """
    错题本模型
    记录用户答错的题目
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wrong_questions'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='wrong_records'
    )
    wrong_count = models.IntegerField(default=1, help_text='答错次数')
    last_wrong_at = models.DateTimeField(auto_now=True, help_text='最后一次答错时间')
    last_score = models.FloatField(help_text='最后一次得分')
    mastered = models.BooleanField(default=False, help_text='是否已掌握')
    mastered_at = models.DateTimeField(null=True, blank=True, help_text='掌握时间')
    notes = models.TextField(blank=True, help_text='用户笔记')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '错题记录'
        verbose_name_plural = '错题记录'
        unique_together = ['user', 'question']
        indexes = [
            models.Index(fields=['user', 'mastered']),
            models.Index(fields=['last_wrong_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.question.title}"

    def increment_wrong_count(self, score):
        """
        增加答错次数
        """
        self.wrong_count += 1
        self.last_score = score
        self.mastered = False
        self.mastered_at = None
        self.save()

    def mark_as_mastered(self):
        """
        标记为已掌握
        """
        from django.utils import timezone
        self.mastered = True
        self.mastered_at = timezone.now()
        self.save()


class UserBehavior(models.Model):
    """
    用户行为追踪模型
    用于分析用户行为模式
    """
    ACTION_TYPES = [
        ('view', '查看'),
        ('answer', '答题'),
        ('favorite', '收藏'),
        ('share', '分享'),
        ('search', '搜索'),
        ('recommend', '推荐'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='behaviors'
    )
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        db_index=True
    )
    target_type = models.CharField(
        max_length=50,
        db_index=True,
        help_text='目标类型：question/category/user'
    )
    target_id = models.IntegerField(db_index=True, help_text='目标ID')
    metadata = models.JSONField(default=dict, blank=True, help_text='额外元数据')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = '用户行为'
        verbose_name_plural = '用户行为'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action_type', 'created_at']),
            models.Index(fields=['target_type', 'target_id']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.action_type} - {self.target_type}:{self.target_id}"
