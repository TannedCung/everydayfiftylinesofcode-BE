from rest_framework import serializers
from core.models.user_activity import UserActivity

class UserActivitySerializer(serializers.ModelSerializer):
    # Optionally include user-related details if needed
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserActivity
        fields = ['id', 'user', 'username', 'date', 'commits', 'modifications']
        read_only_fields = ['id', 'username']
