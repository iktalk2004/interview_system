from django.db import models
from users.models import User
from questions.models import Question


class Interaction(models.Model):
    STATUS_MAP = [
        ('viewed', '仅浏览'),
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('scored', '已评分'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='interactions')
    answer = models.TextField(blank=True)
    score = models.FloatField(null=True)
    time_spent = models.IntegerField(default=0)
    is_submitted = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_MAP, default='viewed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'question', 'is_submitted'],
                condition=models.Q(is_submitted=False),
                name='unique_draft_per_user_question',
            )
        ]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_submitted']),
            models.Index(fields=['question', 'is_submitted']),
            models.Index(fields=['score']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user', 'question']),
        ]

# class History(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     interaction = models.ForeignKey(Interaction, on_delete=models.CASCADE)
#     # 额外字段如 retry_count 如果需要
#     # 额外字段如 retry_count 如果需要
