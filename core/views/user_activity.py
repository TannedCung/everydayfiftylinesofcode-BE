# core/views.py

from rest_framework import viewsets
from .models import Challenge, UserActivity
from .serializers import ChallengeSerializer, UserActivitySerializer

class UserActivityViewSet(viewsets.ModelViewSet):
    queryset = UserActivity.objects.all()
    serializer_class = UserActivitySerializer
