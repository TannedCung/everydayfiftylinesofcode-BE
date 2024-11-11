# api/urls.py
from django.urls import path
from .views.login import user_profile

urlpatterns = [
    path('profile/', user_profile, name='user-profile'),
]
