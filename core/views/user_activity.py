# core/views.py

from rest_framework import viewsets
from rest_framework.viewsets import ReadOnlyModelViewSet
from core.models.github_activity import GitHubEvent, GitHubCommit, GithubFileChange
from core.serializers.github_activity import GitHubEventSerializer, GitHubCommitSerializer, GithubFileChangeSerializer
from core.utils.github import fetch_github_commits, fetch_contribution_calendar, calculate_activity_streak, calculate_daily_goal_progress
from django.http import JsonResponse
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.db.models import Count, Sum, F
from django.utils.timezone import now
from datetime import timedelta, date
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
    @action(detail=False, methods=["get"], url_path="by_day")
    def by_day(self, request):
        """
        Endpoint to get the number of commits and changes in blocks of days.
        Query parameters:
          - `start_date`: The start date for the range (ISO format, e.g., 2024-11-01).
          - `end_date`: The end date for the range (ISO format, e.g., 2024-11-10).
        """
        today = now().date()
        last_30_days = today - timedelta(days=30)

        # Get the date range from the request or default to today and the last 30 days
        start_date = request.query_params.get("start_date", last_30_days.isoformat())
        end_date = request.query_params.get("end_date", today.isoformat())

        start_date = date.fromisoformat(start_date)
        end_date = date.fromisoformat(end_date)

        # Query to aggregate commits and changes by date
        commits_by_day = (
            GitHubCommit.objects.filter(date__gte=start_date, date__lte=end_date)
            .values("date")
            .annotate(
                total_commits=Count("sha"),
                total_changes=Sum(F("additions") + F("deletions")),
            )
            .order_by("date")
        )

        # Create a mapping of existing data
        commits_dict = {
            entry["date"]: {
                "total_commits": entry["total_commits"],
                "total_changes": entry["total_changes"],
            }
            for entry in commits_by_day
        }

        # Generate a list of all dates in the range
        def daterange(start_date, end_date):
            for n in range((end_date - start_date).days + 1):
                yield start_date + timedelta(n)

        # Fill in missing dates with zeros
        data = []
        for single_date in daterange(start_date, end_date):
            date_key = single_date.isoformat()
            if single_date in commits_dict:
                data.append(
                    {
                        "date": date_key,
                        "total_commits": commits_dict[single_date]["total_commits"],
                        "total_changes": commits_dict[single_date]["total_changes"],
                    }
                )
            else:
                data.append(
                    {
                        "date": date_key,
                        "total_commits": 0,
                        "total_changes": 0,
                    }
                )

        return Response(data)

    @action(detail=False, methods=["get"], url_path="activity-streak")
    def activity_streak(self, request):
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

        # Fetch the contribution data from GitHub for the specified year
        contribution_data = fetch_contribution_calendar(user, year)
        if "error" in contribution_data:
            return Response({"error": contribution_data["error"]}, status=400)

        # Calculate the activity streak
        streak_data = calculate_activity_streak(contribution_data["data"]["user"]["contributionsCollection"]["contributionCalendar"], daily_goal)
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
