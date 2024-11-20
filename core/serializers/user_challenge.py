from rest_framework import serializers
from core.models.user_challenge import UserChallenge

class UserChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserChallenge
        fields = ['id', 'user', 'challenge', 'progress', 'start_date']
