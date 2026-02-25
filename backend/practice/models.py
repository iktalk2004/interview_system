from django.db import models
from users.models import User
from questions.models import Question
from core.models import SoftDeleteModel


class Interaction(SoftDeleteModel):
    STATUS_MAP = [
        ('viewed', '仅浏览'),
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('scored', '已评分'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='interactions')
    answer = models.TextField(blank=True)
    score = models.FloatField(null=True, db_index=True)
    time_spent = models.IntegerField(default=0)
    is_submitted = models.BooleanField(default=False, db_index=True)
    is_favorite = models.BooleanField(default=False, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_MAP, default='viewed', db_index=True)
    scoring_method = models.CharField(max_length=50, blank=True, db_index=True)
    feedback = models.TextField(blank=True)
    attempts = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '答题记录'
        verbose_name_plural = '答题记录'
        indexes = [
            models.Index(fields=['user', 'is_submitted']),
            models.Index(fields=['question', 'is_submitted']),
            models.Index(fields=['score']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user', 'question']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['is_favorite']),
            models.Index(fields=['scoring_method']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'question', 'is_submitted'],
                condition=models.Q(is_submitted=False),
                name='unique_draft_per_user_question',
            ),
            models.CheckConstraint(
                check=models.Q(score__gte=0) & models.Q(score__lte=100),
                name='valid_score_range'
            ),
            models.CheckConstraint(
                check=models.Q(time_spent__gte=0),
                name='valid_time_spent'
            ),
            models.CheckConstraint(
                check=models.Q(attempts__gte=1),
                name='valid_attempts'
            ),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.question.title}"

    def increment_attempts(self):
        self.attempts += 1
        self.save(update_fields=['attempts'])

    def mark_as_favorite(self):
        self.is_favorite = True
        self.save(update_fields=['is_favorite'])

    def unmark_as_favorite(self):
        self.is_favorite = False
        self.save(update_fields=['is_favorite'])

# class History(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     interaction = models.ForeignKey(Interaction, on_delete=models.CASCADE)
#     # 额外字段如 retry_count 如果需要
#     # 额外字段如 retry_count 如果需要
