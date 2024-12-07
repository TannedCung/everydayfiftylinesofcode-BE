from django.contrib.auth.models import User
from django.db import models
from core.models.challenge import Challenge
from django.core.validators import MinValueValidator, MaxValueValidator

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

    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} - {self.progress}%"
