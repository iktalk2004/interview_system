from rest_framework import serializers
from .models import UserSimilarity, QuestionSimilarity, Recommendation, UserPreference
from users.serializers import UserSerializer
from questions.serializers import QuestionSerializer


class UserSimilaritySerializer(serializers.ModelSerializer):
    user_a_details = UserSerializer(source='user_a', read_only=True)
    user_b_details = UserSerializer(source='user_b', read_only=True)

    class Meta:
        model = UserSimilarity
        fields = ['id', 'user_a', 'user_b', 'user_a_details', 'user_b_details',
                  'similarity_score', 'common_questions', 'last_updated']


class QuestionSimilaritySerializer(serializers.ModelSerializer):
    question_a_details = QuestionSerializer(source='question_a', read_only=True)
    question_b_details = QuestionSerializer(source='question_b', read_only=True)

    class Meta:
        model = QuestionSimilarity
        fields = ['id', 'question_a', 'question_b', 'question_a_details', 'question_b_details',
                  'similarity_score', 'common_users', 'last_updated']


class RecommendationSerializer(serializers.ModelSerializer):
    question_details = QuestionSerializer(source='question', read_only=True)

    class Meta:
        model = Recommendation
        fields = ['id', 'user', 'question', 'question_details', 'recommendation_type',
                  'score', 'reason', 'is_viewed', 'is_answered', 'created_at']


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ['id', 'user', 'preferred_categories', 'preferred_difficulty',
                  'weak_areas', 'strong_areas', 'avg_score', 'total_answered', 'last_updated']
