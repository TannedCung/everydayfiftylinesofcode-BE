from rest_framework import viewsets
from core.models.club import Club
from core.serializers.club import ClubSerializer
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from core.filters.club import ClubFilter

class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ClubFilter

    def perform_create(self, serializer):
        # Save club with creator
        club = serializer.save(created_by=self.request.user)
        # Add creator as member
        club.members.add(self.request.user)