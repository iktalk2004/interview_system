from django.db import models
from users.models import User
from questions.models import Question


class Interaction(models.Model):  # 交互行为表（用于推荐）
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField(blank=True)  # 用户答案
    score = models.FloatField(null=True)  # 评分（0-10）
    time_spent = models.IntegerField(default=0)  # 时长（秒）
    is_favorite = models.BooleanField(default=False)  # 收藏
    created_at = models.DateTimeField(auto_now_add=True)


class History(models.Model):  # 历史记录（可选）
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    interaction = models.ForeignKey(Interaction, on_delete=models.CASCADE)
    # 额外字段如 retry_count 如果需要
    # 额外字段如 retry_count 如果需要
