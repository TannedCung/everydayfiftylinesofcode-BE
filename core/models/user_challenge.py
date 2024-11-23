from django.contrib.auth.models import User
from django.db import models
from core.models.challenge import Challenge

class UserChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    start_date = models.DateField()
    progress = models.IntegerField(default=0)