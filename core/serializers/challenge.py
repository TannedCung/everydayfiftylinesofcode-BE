from rest_framework import serializers
from core.models.challenge import Challenge

class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ['id', 'name', 'description', 'commitment_type', 'frequency', 'start_date', 'end_date']
