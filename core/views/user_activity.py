# core/views.py

from rest_framework import viewsets
from rest_framework.viewsets import ReadOnlyModelViewSet
from core.models.github_activity import GitHubEvent, GitHubCommit, GithubFileChange
from core.serializers.github_activity import GitHubEventSerializer, GitHubCommitSerializer, GithubFileChangeSerializer
from core.tasks.sync_challenges import update_user_challenges
from core.tasks.sync_commit_data import update_github_commits
from core.utils.github import fetch_commits_with_changes, fetch_github_commits, fetch_contribution_calendar, calculate_activity_streak, calculate_daily_goal_progress
from django.http import JsonResponse
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.db.models import Count, Sum, F
from django.utils.timezone import now
from django.utils import timezone
from datetime import timedelta, date, datetime
from drf_spectacular.utils import extend_schema, OpenApiParameter

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
            "within the specified date range. Defaults to the last 30 days if no dates are provided."
        ),
        parameters=[
            OpenApiParameter(
                name="start_date",
                description="Start date for the range (ISO 8601 format, e.g., '2024-01-01'). Defaults to 30 days ago.",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="end_date",
                description="End date for the range (ISO 8601 format, e.g., '2024-12-31'). Defaults to today.",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={200: None},  # Replace `None` with your response serializer if needed
    )
    @action(detail=False, methods=["get"], url_path="commits-with-changes")
    def commits_with_changes(self, request):
        """
        Endpoint to fetch commits along with their changes grouped by day.
        Query parameters:
        - `start_date`: Optional start date for the range (defaults to 30 days ago if not provided).
        - `end_date`: Optional end date for the range (defaults to today if not provided).
        """
        user = request.user
        
        # Get today's date and calculate the date 30 days ago
        today = datetime.today()
        default_start_date = (today - timedelta(days=30)).date().strftime('%Y-%m-%d')
        default_end_date = today.date().strftime('%Y-%m-%d')

        # Retrieve dates from query parameters or use defaults
        start_date = request.query_params.get("start_date", default_start_date)
        end_date = request.query_params.get("end_date", default_end_date)

        # Ensure the dates are in the correct format (ISO 8601)
        try:
            start_date = datetime.fromisoformat(start_date).date()
            end_date = datetime.fromisoformat(end_date).date()
        except ValueError:
            return Response({"error": "Invalid date format. Please use ISO 8601 format (e.g., '2024-01-01')."}, status=400)

        # Fetch commits with changes using the utility function
        commit_data = fetch_commits_with_changes(user, start_date, end_date)

        if "error" in commit_data:
            return Response({"error": commit_data["error"]}, status=400)

        update_github_commits.delay(user.id, commit_data)
        return Response(commit_data)

    @action(detail=False, methods=["get"], url_path="activity-streak")
    def activity_streak(self, request):
        def get_current_day():
            today = now()
            first_day = timezone.make_aware(datetime(2024, 1, 1), timezone.get_current_timezone())
            return (today - first_day).days + 1
        """
        Endpoint to retrieve the current and longest streak of coding activity.
        Query parameters:
          - `year`: The year for which to fetch the contribution calendar (optional).
        """
        user = request.user
        daily_goal = 1
        year = request.query_params.get("year", None)

        # Validate the year parameter (if provided)
        if year:
            try:
                year = int(year)
            except ValueError:
                return Response({"error": "Invalid year format."}, status=400)
        else:
            # If no year is provided, use the current year
            year = now().year
        today_th = None
        if year == now().year:
            today_th = get_current_day()

        # Fetch the contribution data from GitHub for the specified year
        contribution_data = fetch_contribution_calendar(user, year)
        if "error" in contribution_data:
            return Response({"error": contribution_data["error"]}, status=400)

        # Calculate the activity streak
        streak_data = calculate_activity_streak(contribution_data["data"]["user"]["contributionsCollection"]["contributionCalendar"], daily_goal, today_th)
        return Response(streak_data)

    @action(detail=False, methods=["get"], url_path="daily-goal-progress")
    def daily_goal_progress(self, request):
        """
        Endpoint to retrieve daily progress towards a goal.
        Query parameters:
          - `daily_goal`: The user's daily goal (integer, default: 1).
          - `year`: The year for which to fetch the contribution calendar (optional).
        """
        user = request.user
        daily_goal = int(request.query_params.get("daily_goal", 1))
        year = request.query_params.get("year", None)

        # Validate the year parameter (if provided)
        if year:
            try:
                year = int(year)
            except ValueError:
                return Response({"error": "Invalid year format."}, status=400)
        else:
            # If no year is provided, use the current year
            year = now().year

        # Fetch the contribution data from GitHub for the specified year
        contribution_data = fetch_contribution_calendar(user, year)
        if "error" in contribution_data:
            return Response({"error": contribution_data["error"]}, status=400)

        # Calculate the daily goal progress
        progress_data = calculate_daily_goal_progress(
            contribution_data["data"]["user"]["contributionsCollection"]["contributionCalendar"], daily_goal
        )
        return Response(progress_data)

    @extend_schema(
        summary="The year for getting th graph",
        description=(
            "Retrieve the total number of commits and changes grouped by day "
            "within the specified date range. Defaults to the current year if no dates are provided."
        ),
        parameters=[
            OpenApiParameter(
                name="year",
                description="",
                required=False,
                type=int,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={200: None},  # Replace `None` with your response serializer if needed
    )
    @action(detail=False, methods=["get"], url_path="contribution-calendar")
    def contribution_calendar(self, request):
        """
        Endpoint to retrieve the user's GitHub contribution calendar for a specific year.
        Query parameters:
          - `year`: The year for which to fetch the contribution calendar (e.g., 2024).
        """
        user = request.user
        year = request.query_params.get("year", None)

        # Validate the year parameter
        if year:
            try:
                year = int(year)
            except ValueError:
                return Response({"error": "Invalid year format."}, status=400)
        else:
            # If no year is provided, return the current year
            year = now().year

        # Fetch the contribution data from GitHub
        contribution_data = fetch_contribution_calendar(user, year)
        if "error" in contribution_data:
            return Response({"error": contribution_data["error"]}, status=400)
        
        # update_user_challenges.delay(
        #     user.id, 
        #     contribution_data
        # )
        return Response(contribution_data)


class GithubFileChangeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing or retrieving GitHub file changes.
    """
    queryset = GithubFileChange.objects.all()
    serializer_class = GithubFileChangeSerializer


@api_view(["GET"])
def get_user_commits(request):
    """
    Fetch and sync GitHub commits for the authenticated user.
    """
    user = request.user
    commits = fetch_github_commits(user)
    return JsonResponse(commits, safe=False)
