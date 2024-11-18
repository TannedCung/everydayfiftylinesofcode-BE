# api/urls.py
from django.urls import path
from .views.login import user_profile, github_callback
from .views.user_activity import get_user_commits

urlpatterns = [
    path('profile/', user_profile, name='user-profile'),
    path('accounts/github/callback/', github_callback, name='github-callback'),
    path('github/commits/', get_user_commits, name='get_user_commits'),
]

