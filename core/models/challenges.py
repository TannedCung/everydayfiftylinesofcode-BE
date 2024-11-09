from django.contrib.auth.models import User
from django.db import models

class Challenge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    min_commits_per_day = models.IntegerField(null=True, blank=True)
    min_modifications_per_day = models.IntegerField(null=True, blank=True)
    duration_days = models.IntegerField()
    participants = models.ManyToManyField(User, through='UserChallenge')