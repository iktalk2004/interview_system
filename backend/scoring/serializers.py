from rest_framework import serializers
from .models import ScoringHistory
from practice.serializers import InteractionSerializer


class ScoringHistorySerializer(serializers.ModelSerializer):
    interaction_details = InteractionSerializer(source='interaction', read_only=True)

    class Meta:
        model = ScoringHistory
        fields = ['id', 'interaction', 'interaction_details', 'scoring_method',
                  'score', 'details', 'created_at']
