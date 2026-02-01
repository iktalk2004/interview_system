from rest_framework import serializers
from .models import Interaction


class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = ['id', 'user', 'question', 'answer', 'score', 'time_spent', 'is_favorite', 'created_at', 'status']
        read_only_fields = ('user', 'created_at')
