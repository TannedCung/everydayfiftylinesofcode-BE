from rest_framework.viewsets import ModelViewSet
from core.models.user_challenge import UserChallenge
from core.models.github_activity import GitHubCommit, GitHubEvent, GithubFileChange
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.decorators import action
from core.serializers.user_challenge import UserChallengeSerializer
from rest_framework.permissions import IsAuthenticated
from django.db import models

class UserChallengeViewSet(ModelViewSet):
    queryset = UserChallenge.objects.all()
    serializer_class = UserChallengeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return challenges for the authenticated user only.
        """
        return UserChallenge.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Automatically associate the user with the created challenge.
        """
        serializer.save(user=self.request.user, start_date=now().date())
    
    @action(detail=True, methods=['post'], url_path='update-progress')
    def update_progress(self, request, pk=None):
        """
        Update the progress of a user's challenge based on the challenge type and user activity.
        """
        user_challenge = self.get_object()
        challenge = user_challenge.challenge
        user = self.request.user

        today = now().date()
        if challenge.end_date and today > challenge.end_date:
            return Response({
                "message": "Challenge already finished",
                "progress": user_challenge.progress,
                "progress_detail": user_challenge.progress_detail,
            })

        progress_detail = []
        # Daily Challenge Progress Calculation
        if challenge.commitment_by == "daily":
            if challenge.end_date:
                challenge_span = (challenge.end_date - challenge.start_date).days + 1
            else:
                challenge_span = (today - challenge.start_date).days + 1

            # Query commits directly from the GitHubCommit table
            commits_by_day = (
                GitHubCommit.objects.filter(
                    github_event__user=user,
                    date__gte=challenge.start_date,
                    date__lte=today
                )
                .values("date")
                .annotate(
                    total_commits=models.Count("sha"),
                    total_changes=models.Sum(models.F("additions") + models.F("deletions"))
                ).order_by("date")
            )

            # Calculate active days meeting the frequency condition
            active_days = 0
            consecutive_days = 0
            for commit in commits_by_day:
                progress_detail.append({**commit, "date": commit["date"].isoformat()})
                metric = commit["total_commits"] if challenge.type == "commits" else commit["total_changes"]
                if metric >= challenge.frequency:
                    active_days += 1
                    consecutive_days += 1
                else:
                    consecutive_days = 0  # Reset streak if condition not met

            if user_challenge.highest_streak < consecutive_days:
                user_challenge.highest_streak = consecutive_days

            # Calculate progress as active_days / elapsed_days
            progress = (consecutive_days / challenge_span) * 100
            user_challenge.progress = min(100, progress)

        # Accumulate Challenge Progress Calculation
        elif challenge.commitment_by == "accumulate":
            # Query all commits by the user
            progress_detail = user_challenge.progress_detail
            commits = GitHubCommit.objects.filter(
                github_event__user=user,
                date__gte=challenge.start_date,
                date__lte=challenge.end_date or today
            )
            if challenge.type == "commits":
                total_commits = commits.count()
                progress = (total_commits / challenge.target_value) * 100
            elif challenge.type == "lines_of_code":
                total_changes = commits.aggregate(
                    total_changes=models.Sum(models.F("additions") + models.F("deletions"))
                )["total_changes"] or 0
                progress = (total_changes / challenge.target_value) * 100
            user_challenge.progress = min(100, progress)
            progress_detail.append({"date": now().date().isoformat(),
                                    "progress": user_challenge.progress})

        # Accumulate progress_detail by date
        user_challenge.progress_detail = progress_detail
        user_challenge.save()

        return Response({
            "message": "Progress updated successfully.",
            "progress": user_challenge.progress,
            "progress_detail": user_challenge.progress_detail,
        })
