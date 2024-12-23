# core/views/club.py
from rest_framework import viewsets
from core.models.club import Club
from core.serializers.club import ClubSerializer
from rest_framework.permissions import IsAuthenticated

class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally restricts the returned clubs to those the user is a member of,
        by filtering against a `member` query parameter in the URL.
        """
        queryset = Club.objects.all()
        user = self.request.user
        if user:
            queryset = queryset.filter(members=user)
        return queryset