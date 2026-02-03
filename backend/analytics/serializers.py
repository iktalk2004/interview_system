from rest_framework import serializers
from .models import UserStats, CategoryStats, DailyStats, PerformanceTrend
from users.serializers import UserSerializer
from questions.serializers import QuestionSerializer, CategorySerializer


class UserStatsSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = UserStats
        fields = ['id', 'user', 'user_details', 'total_questions_answered', 'total_questions_viewed',
                  'average_score', 'highest_score', 'lowest_score', 'total_time_spent',
                  'average_time_per_question', 'favorite_count', 'last_activity']


class CategoryStatsSerializer(serializers.ModelSerializer):
    category_details = CategorySerializer(source='category', read_only=True)
    most_difficult_details = QuestionSerializer(source='most_difficult', read_only=True)
    easiest_details = QuestionSerializer(source='easiest', read_only=True)

    class Meta:
        model = CategoryStats
        fields = ['id', 'category', 'category_details', 'total_questions', 'total_answers',
                  'average_score', 'most_difficult', 'most_difficult_details', 'easiest',
                  'easiest_details', 'last_updated']


class DailyStatsSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = DailyStats
        fields = ['id', 'date', 'user', 'user_details', 'questions_answered',
                  'questions_viewed', 'average_score', 'time_spent']


class PerformanceTrendSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = PerformanceTrend
        fields = ['id', 'user', 'user_details', 'date', 'score_trend',
                  'accuracy_trend', 'speed_trend']
