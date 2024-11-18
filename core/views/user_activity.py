# core/views.py

from rest_framework import viewsets
from core.models.user_activity import UserActivity
from core.serializers.user_activity import UserActivitySerializer
from core.utils.github import fetch_github_commits
import requests
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view

class UserActivityViewSet(viewsets.ModelViewSet):
    queryset = UserActivity.objects.all()
    serializer_class = UserActivitySerializer

@api_view(['GET'])
def get_user_commits(request):
    user = request.user
    commits = fetch_github_commits(user)
    print(f"[DEBUG]: commit", commits)
    return JsonResponse(commits, safe=False)