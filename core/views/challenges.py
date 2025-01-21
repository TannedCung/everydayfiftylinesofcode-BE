# challenges.py
from core.permissions.member_management import MemberManagementMixin
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from core.models.challenge import Challenge
from core.serializers.challenge import ChallengeSerializer
from core.filters.challenge import ChallengeFilter
from core.serializers.challenge import ChallengeUserSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from core.models.user_challenge import UserChallenge

class ChallengeViewSet(MemberManagementMixin, viewsets.ModelViewSet):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ChallengeFilter

    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        challenge = get_object_or_404(Challenge, pk=pk)
        
        # Query UserChallenge directly
        user_challenges = UserChallenge.objects.filter(
            challenge=challenge
        ).select_related(
            'user'
        ).order_by(
            '-progress',
            '-highest_streak'
        )

        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(user_challenges, request)
        
        serializer = ChallengeUserSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)