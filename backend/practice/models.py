from django.db import models
from users.models import User
from questions.models import Question


class Interaction(models.Model):  # 交互行为表（用于推荐）
    STATUS_MAP = [
        ('viewed', '仅浏览'),  # 只浏览，未输入答案
        ('draft', '草稿'),  # 输入了部分答案，未正式提交
        ('submitted', '已提交'),  # 用户点击提交答案
        ('scored', '已评分'),  # 后端/人工评分完成
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField(blank=True)  # 用户答案
    score = models.FloatField(null=True)  # 评分（0-10）
    time_spent = models.IntegerField(default=0)  # 时长（秒）
    is_submitted = models.BooleanField(default=False)  # 是否提交
    is_favorite = models.BooleanField(default=False)  # 收藏
    status = models.CharField(max_length=20, choices=STATUS_MAP, default='viewed')  # 状态
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

# class History(models.Model):  # 历史记录（可选）
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     interaction = models.ForeignKey(Interaction, on_delete=models.CASCADE)
#     # 额外字段如 retry_count 如果需要
#     # 额外字段如 retry_count 如果需要
