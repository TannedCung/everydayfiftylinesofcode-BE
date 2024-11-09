from rest_framework import viewsets
from .models import Challenge, UserActivity
from .serializers import ChallengeSerializer, UserActivitySerializer

class ChallengeViewSet(viewsets.ModelViewSet):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer