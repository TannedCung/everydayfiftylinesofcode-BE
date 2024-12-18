from rest_framework.viewsets import ModelViewSet
from core.models.user_challenge import UserChallenge
from core.models.github_activity import GitHubCommit, GitHubEvent, GithubFileChange
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.decorators import action
from core.serializers.user_challenge import UserChallengeSerializer
from rest_framework.permissions import IsAuthenticated
from django.db import models
from django.db import IntegrityError
from rest_framework import status
from core.filters.user_challenge import UserChallengeFilter
from django_filters.rest_framework import DjangoFilterBackend

class UserChallengeViewSet(ModelViewSet):
    queryset = UserChallenge.objects.all()
    serializer_class = UserChallengeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserChallengeFilter

    def get_queryset(self):
        """
        Return challenges for the authenticated user only.
        """
        return UserChallenge.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED, 
                headers=headers
            )
        except IntegrityError:
            return Response(
                {"error": "You have already joined this challenge"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        """
        Automatically associate the user with the created challenge.
        """
        serializer.save(user=self.request.user, start_date=now().date())
    
    @action(detail=True, methods=['post'], url_path='update-progress')
    def update_progress(self, request, pk=None):
        """
        Update the progress of a user's challenge
        """
        user_challenge = self.get_object()
        result = user_challenge.update_progress()
        return Response(result)
