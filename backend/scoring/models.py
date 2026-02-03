from django.db import models
from practice.models import Interaction


class ScoringHistory(models.Model):
    """
    评分历史模型
    记录每次评分的详细信息
    """
    SCORING_METHODS = [
        ('embedding', '基于嵌入的评分'),
        ('llm', '基于大语言模型的评分'),
        ('manual', '人工评分'),
    ]

    interaction = models.ForeignKey(Interaction, on_delete=models.CASCADE, related_name='scoring_history')
    scoring_method = models.CharField(max_length=20, choices=SCORING_METHODS)
    score = models.FloatField()
    details = models.JSONField(default=dict, blank=True)  # 评分详细信息
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['interaction']),
            models.Index(fields=['scoring_method']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.interaction.user.username} - {self.scoring_method}: {self.score}"
