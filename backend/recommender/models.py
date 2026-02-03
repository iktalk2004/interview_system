from django.db import models
from users.models import User
from questions.models import Question


class UserSimilarity(models.Model):
    """
    用户相似度模型 - 用于基于用户的协同过滤
    存储用户之间的相似度分数
    """
    user_a = models.ForeignKey(User, on_delete=models.CASCADE, related_name='similarity_as_a')
    user_b = models.ForeignKey(User, on_delete=models.CASCADE, related_name='similarity_as_b')
    similarity_score = models.FloatField(default=0.0)  # 相似度分数，范围 0-1
    common_questions = models.IntegerField(default=0)  # 共同答题数量
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user_a', 'user_b']
        indexes = [
            models.Index(fields=['user_a']),
            models.Index(fields=['user_b']),
            models.Index(fields=['similarity_score']),
        ]

    def __str__(self):
        return f"{self.user_a.username} - {self.user_b.username}: {self.similarity_score:.2f}"


class QuestionSimilarity(models.Model):
    """
    题目相似度模型 - 用于基于物品的协同过滤
    存储题目之间的相似度分数
    """
    question_a = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='similarity_as_a')
    question_b = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='similarity_as_b')
    similarity_score = models.FloatField(default=0.0)  # 相似度分数，范围 0-1
    common_users = models.IntegerField(default=0)  # 共同答题用户数量
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['question_a', 'question_b']
        indexes = [
            models.Index(fields=['question_a']),
            models.Index(fields=['question_b']),
            models.Index(fields=['similarity_score']),
        ]

    def __str__(self):
        return f"Q{self.question_a.id} - Q{self.question_b.id}: {self.similarity_score:.2f}"


class Recommendation(models.Model):
    """
    推荐记录模型 - 记录给用户的推荐结果
    """
    RECOMMENDATION_TYPES = [
        ('user_based', '基于用户的协同过滤'),
        ('item_based', '基于物品的协同过滤'),
        ('hybrid', '混合推荐'),
        ('content_based', '基于内容的推荐'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='recommendations')
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES, default='hybrid')
    score = models.FloatField(default=0.0)  # 推荐分数，用于排序
    reason = models.TextField(blank=True)  # 推荐理由
    is_viewed = models.BooleanField(default=False)  # 是否已查看
    is_answered = models.BooleanField(default=False)  # 是否已答题
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score', '-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['question']),
            models.Index(fields=['score']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - Q{self.question.id}: {self.score:.2f}"


class UserPreference(models.Model):
    """
    用户偏好模型 - 基于用户答题历史计算的用户偏好
    用于个性化推荐
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preference_profile')
    preferred_categories = models.JSONField(default=dict)  # 偏好的分类及其权重
    preferred_difficulty = models.JSONField(default=dict)  # 偏好的难度及其权重
    weak_areas = models.JSONField(default=list)  # 薄弱领域（分类列表）
    strong_areas = models.JSONField(default=list)  # 强项领域（分类列表）
    avg_score = models.FloatField(default=0.0)  # 平均分数
    total_answered = models.IntegerField(default=0)  # 总答题数
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Avg Score: {self.avg_score:.2f}"
