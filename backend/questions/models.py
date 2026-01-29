from django.db import models
from users.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)


class Question(models.Model):
    title = models.CharField(max_length=200)
    answer = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    difficulty = models.IntegerField(default=1)  # 1-3 对应 易 中 难
    is_approved = models.BooleanField(default=False)
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
