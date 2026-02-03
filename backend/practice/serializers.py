from rest_framework import serializers
from .models import Interaction
from questions.serializers import QuestionSerializer


class InteractionSerializer(serializers.ModelSerializer):
    question_details = QuestionSerializer(source='question', read_only=True)

    class Meta:
        model = Interaction
        fields = ['id', 'user', 'question', 'question_details', 'answer', 'score', 'time_spent', 'is_favorite', 'created_at', 'status']
        read_only_fields = ('user', 'created_at')
