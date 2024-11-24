from rest_framework import serializers
from core.models.user_challenge import UserChallenge
from core.models.challenge import Challenge  # Assuming Challenge is imported from core

class UserChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserChallenge
        fields = ['id', 'challenge', 'start_date', 'progress', 'progress_detail', 'highest_streak']  # Include all fields
        read_only_fields = ('progress', 'progress_detail', 'start_date', 'highest_streak')  # Progress is updated by the system
