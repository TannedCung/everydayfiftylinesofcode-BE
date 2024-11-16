# api/urls.py
from django.urls import path
from .views.login import user_profile, github_callback

urlpatterns = [
    path('profile/', user_profile, name='user-profile'),
    path('accounts/github/callback/', github_callback, name='github-callback'),

    
]

