# challenges.py
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from core.models.challenge import Challenge
from core.serializers.challenge import ChallengeSerializer
from core.filters.challenge import ChallengeFilter

class ChallengeViewSet(viewsets.ModelViewSet):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ChallengeFilter