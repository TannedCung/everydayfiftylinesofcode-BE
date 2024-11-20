from rest_framework import serializers
from core.models.github_activity import GitHubActivityLog

class GitHubActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = GitHubActivityLog
        fields = ['id', 'user', 'date', 'event_type', 'repo', 'commits']