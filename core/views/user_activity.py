# core/views.py

from rest_framework import viewsets
from rest_framework.viewsets import ReadOnlyModelViewSet
from core.models.github_activity import GitHubEvent, GitHubCommit, GithubFileChange
from core.serializers.github_activity import GitHubEventSerializer, GitHubCommitSerializer, GithubFileChangeSerializer
from core.utils.github import fetch_github_commits
import requests
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, F
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

class GitHubEventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing or retrieving GitHub events.
    """
    queryset = GitHubEvent.objects.all()
    serializer_class = GitHubEventSerializer


class GitHubCommitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing or retrieving GitHub commits.
    """
    queryset = GitHubCommit.objects.all()
    serializer_class = GitHubCommitSerializer


    @extend_schema(
        summary="Get commits and changes by day",
        description=(
            "Retrieve the total number of commits and changes grouped by day "
            "within the specified date range. Defaults to the current year if no dates are provided."
        ),
        parameters=[
            OpenApiParameter(
                name="start_date",
                description="Start date for the range (ISO 8601 format, e.g., '2024-01-01'). Defaults to January 1 of the current year.",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="end_date",
                description="End date for the range (ISO 8601 format, e.g., '2024-12-31'). Defaults to December 31 of the current year.",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={200: None},  # Replace `None` with your response serializer if needed
    )
    @action(detail=False, methods=['get'], url_path='by_day')
    def by_day(self, request):
        """
        Endpoint to get the number of commits and changes in blocks of days.
        Query parameters:
          - `start_date`: The start date for the range (ISO format, e.g., 2024-11-01).
          - `end_date`: The end date for the range (ISO format, e.g., 2024-11-10).
        """ 
        today = now().date()
        current_year_start = today.replace(month=1, day=1)
        current_year_end = today.replace(month=12, day=31)

        start_date = request.query_params.get('start_date', current_year_start.isoformat())
        end_date = request.query_params.get('end_date', current_year_end.isoformat())

        # Query to aggregate commits and changes by date
        commits_by_day = (
            GitHubCommit.objects.filter(date__gte=start_date, date__lte=end_date)
            .values('date')
            .annotate(
                total_commits=Count('sha'),
                total_changes=Sum(F('additions') + F('deletions'))
            )
            .order_by('date')
        )

        # Transform results into a list of dictionaries
        data = [
            {
                "date": entry['date'].isoformat(),
                "total_commits": entry['total_commits'],
                "total_changes": entry['total_changes'],
            }
            for entry in commits_by_day
        ]

        return Response(data)


class GithubFileChangeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing or retrieving GitHub file changes.
    """
    queryset = GithubFileChange.objects.all()
    serializer_class = GithubFileChangeSerializer


@api_view(['GET'])
def get_user_commits(request):
    user = request.user
    commits = fetch_github_commits(user)
    print(f"[DEBUG]: commit", commits)
    return JsonResponse(commits, safe=False)