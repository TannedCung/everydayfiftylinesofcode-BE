from rest_framework import serializers
from core.models.challenge import Challenge

class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ['id', 'name', 'type', 'description', 'target_value', 'start_date', 'end_date']
