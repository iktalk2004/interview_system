from rest_framework import serializers
from .models import Category, Question


class CategorySerializer(serializers.ModelSerializer):
    """
        分类序列化器
    """

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent']


class QuestionSerializer(serializers.ModelSerializer):
    """
        题目序列化器
    """
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'title', 'answer', 'category', 'creator', 'difficulty', 'is_approved', 'created_at',
                  'explanation']
