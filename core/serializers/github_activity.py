from rest_framework import serializers
from core.models.github_activity import GitHubEvent, GitHubCommit, GithubFileChange


class GithubFileChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GithubFileChange
        fields = [
            'sha',
            'filename',
            'status',
            'additions',
            'deletions',
            'changes',
            'blob_url',
            'raw_url',
            'contents_url',
        ]


class GitHubCommitSerializer(serializers.ModelSerializer):
    file_changes = GithubFileChangeSerializer(many=True, read_only=True, source='githubfilechange_set')

    class Meta:
        model = GitHubCommit
        fields = [
            'sha',
            'github_event',
            'author',
            'message',
            'url',
            'file_changes',
        ]


class GitHubEventSerializer(serializers.ModelSerializer):
    commits = GitHubCommitSerializer(many=True, read_only=True, source='githubcommit_set')

    class Meta:
        model = GitHubEvent
        fields = [
            'user',
            'date',
            'event_type',
            'repo',
            'commits',
        ]
