from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.login import user_profile, github_callback
from .views.user_activity import get_user_commits, GitHubEventViewSet, GitHubCommitViewSet, GithubFileChangeViewSet
from .views.challenges import ChallengeViewSet

# Define a router for the viewsets
router = DefaultRouter()
router.register(r'github/events', GitHubEventViewSet, basename='event')
router.register(r'github/commits', GitHubCommitViewSet, basename='commit')
router.register(r'github/changes', GithubFileChangeViewSet, basename='change')

router.register(f'challenge', ChallengeViewSet, basename='challenge')

# Add other non-viewset endpoints
urlpatterns = [
    path('profile/', user_profile, name='user-profile'),
    path('accounts/github/callback/', github_callback, name='github-callback'),
    path('github/sync_commits/', get_user_commits, name='get_user_commits'),
    path('', include(router.urls)),  # Include the router-generated routes
]
