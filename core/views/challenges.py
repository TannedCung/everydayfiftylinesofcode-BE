from rest_framework import viewsets
from core.models.challenge import Challenge
from core.serializers.challenge import ChallengeSerializer

class ChallengeViewSet(viewsets.ModelViewSet):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer