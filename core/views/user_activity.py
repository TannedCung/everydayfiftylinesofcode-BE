# core/views.py

from rest_framework import viewsets
from rest_framework.viewsets import ReadOnlyModelViewSet
from core.models.github_activity import GitHubEvent, GitHubCommit, GithubFileChange
from core.serializers.github_activity import GitHubEventSerializer, GitHubCommitSerializer, GithubFileChangeSerializer
from core.utils.github import fetch_github_commits
import requests
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view


class GitHubEventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing or retrieving GitHub events.
    """
    queryset = GitHubEvent.objects.all()
    serializer_class = GitHubEventSerializer


class GitHubCommitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing or retrieving GitHub commits.
    """
    queryset = GitHubCommit.objects.all()
    serializer_class = GitHubCommitSerializer


class GithubFileChangeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing or retrieving GitHub file changes.
    """
    queryset = GithubFileChange.objects.all()
    serializer_class = GithubFileChangeSerializer


@api_view(['GET'])
def get_user_commits(request):
    user = request.user
    commits = fetch_github_commits(user)
    print(f"[DEBUG]: commit", commits)
    return JsonResponse(commits, safe=False)