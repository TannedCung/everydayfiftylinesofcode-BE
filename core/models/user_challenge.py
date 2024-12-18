from django.contrib.auth.models import User
from django.db import models
from core.models.challenge import Challenge
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import now

from core.models.github_activity import GitHubCommit

class UserChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    start_date = models.DateField()
    highest_streak = models.PositiveIntegerField(default=0)
    progress = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    progress_detail = models.JSONField(default=dict)  # Added JSONField for detailed progress tracking
    
    class Meta:
        unique_together = ['user', 'challenge']
        indexes = [
            models.Index(fields=['user', 'challenge']),  # Composite index
            models.Index(fields=['progress']),  # Index for sorting/filtering by progress
        ]

    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} - {self.progress}%"

    def update_progress(self):
        """
        Update progress based on challenge type and user activity
        """
        challenge = self.challenge
        user = self.user
        today = now().date()

        if challenge.end_date and today > challenge.end_date:
            return {
                "message": "Challenge already finished",
                "progress": self.progress,
                "progress_detail": self.progress_detail,
            }

        progress_detail = []
        
        # Daily Challenge Progress Calculation
        if challenge.commitment_by == "daily":
            challenge_span = ((challenge.end_date or today) - challenge.start_date).days + 1

            commits_by_day = (
                GitHubCommit.objects.filter(
                    github_event__user=user,
                    date__gte=challenge.start_date,
                    date__lte=today
                )
                .values("date")
                .annotate(
                    total_commits=models.Count("oid"),
                    total_changes=models.Sum(models.F("additions") + models.F("deletions"))
                ).order_by("date")
            )

            active_days = 0
            consecutive_days = 0
            for commit in commits_by_day:
                progress_detail.append({**commit, "date": commit["date"].isoformat()})
                metric = commit["total_commits"] if challenge.type == "commits" else commit["total_changes"]
                if metric >= challenge.frequency:
                    active_days += 1
                    consecutive_days += 1
                else:
                    consecutive_days = 0

            self.highest_streak = max(self.highest_streak, consecutive_days)
            self.progress = min(100, (consecutive_days / challenge_span) * 100)

        # Accumulate Challenge Progress Calculation
        elif challenge.commitment_by == "accumulate":
            progress_detail = self.progress_detail
            commits = GitHubCommit.objects.filter(
                github_event__user=user,
                date__gte=challenge.start_date,
                date__lte=challenge.end_date or today
            )
            
            if challenge.type == "commits":
                total_commits = commits.count()
                progress = (total_commits / challenge.target_value) * 100
            else:  # lines_of_code
                total_changes = commits.aggregate(
                    total_changes=models.Sum(models.F("additions") + models.F("deletions"))
                )["total_changes"] or 0
                progress = (total_changes / challenge.target_value) * 100
                
            self.progress = min(100, progress)
            progress_detail.append({
                "date": today.isoformat(),
                "progress": self.progress
            })

        self.progress_detail = progress_detail
        self.save()

        return {
            "message": "Progress updated successfully",
            "progress": self.progress,
            "progress_detail": self.progress_detail,
        }
    