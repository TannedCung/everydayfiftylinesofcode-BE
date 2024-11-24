from django.contrib.auth.models import User
from django.db import models

class Challenge(models.Model):
    TYPE_CHOICES = [
        ('commits', 'Commits'),
        ('lines_of_code', 'Lines of Code'),
    ]

    COMMITMENT_CHOICES = [
        ('daily', 'Daily'),
        ('accumulate', 'Accumulate'),
    ]

    name = models.CharField(max_length=255)  # e.g., "Daily Commit Challenge"
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)  # Type of challenge
    commitment_by = models.CharField(max_length=20, choices=COMMITMENT_CHOICES)
    description = models.TextField()  # Changed to TextField for flexibility
    target_value = models.PositiveIntegerField(default=0)  # e.g., total 100 commits
    frequency = models.PositiveIntegerField(default=0)  # e.g., 5 commits/day
    start_date = models.DateField()  # When the challenge starts
    end_date = models.DateField(null=True, blank=True)  # Optional end date
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"
