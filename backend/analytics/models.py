from django.db import models
from users.models import User
from questions.models import Question, Category


class UserStats(models.Model):
    """
    用户统计数据模型
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='stats')
    total_questions_answered = models.IntegerField(default=0)  # 总答题数
    total_questions_viewed = models.IntegerField(default=0)  # 总浏览数
    average_score = models.FloatField(default=0.0)  # 平均分数
    highest_score = models.FloatField(default=0.0)  # 最高分数
    lowest_score = models.FloatField(default=0.0)  # 最低分数
    total_time_spent = models.IntegerField(default=0)  # 总用时（秒）
    average_time_per_question = models.FloatField(default=0.0)  # 平均每题用时（秒）
    favorite_count = models.IntegerField(default=0)  # 收藏数量
    last_activity = models.DateTimeField(auto_now=True)  # 最后活动时间

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['-average_score']),
            models.Index(fields=['-total_questions_answered']),
        ]

    def __str__(self):
        return f"{self.user.username} - 答题数: {self.total_questions_answered}, 平均分: {self.average_score:.2f}"


class CategoryStats(models.Model):
    """
    分类统计数据模型
    """
    category = models.OneToOneField(Category, on_delete=models.CASCADE, related_name='stats')
    total_questions = models.IntegerField(default=0)  # 该分类题目总数
    total_answers = models.IntegerField(default=0)  # 该分类总答题数
    average_score = models.FloatField(default=0.0)  # 该分类平均分
    most_difficult = models.ForeignKey(
        Question, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='most_difficult_in_category'
    )  # 最难的题目
    easiest = models.ForeignKey(
        Question, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='easiest_in_category'
    )  # 最简单的题目
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['-average_score']),
        ]

    def __str__(self):
        return f"{self.category.name} - 答题数: {self.total_answers}, 平均分: {self.average_score:.2f}"


class DailyStats(models.Model):
    """
    每日统计数据模型
    """
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_stats')
    questions_answered = models.IntegerField(default=0)  # 当日答题数
    questions_viewed = models.IntegerField(default=0)  # 当日浏览数
    average_score = models.FloatField(default=0.0)  # 当日平均分
    time_spent = models.IntegerField(default=0)  # 当日用时（秒）

    class Meta:
        unique_together = ['date', 'user']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['user']),
            models.Index(fields=['-date']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.date}: 答题 {self.questions_answered} 题"


class PerformanceTrend(models.Model):
    """
    性能趋势模型
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performance_trends')
    date = models.DateField()
    score_trend = models.FloatField(default=0.0)  # 分数趋势（相对于前一天的分数变化）
    accuracy_trend = models.FloatField(default=0.0)  # 准确率趋势
    speed_trend = models.FloatField(default=0.0)  # 速度趋势（答题速度变化）

    class Meta:
        unique_together = ['user', 'date']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.date}: 分数趋势 {self.score_trend:+.2f}"
