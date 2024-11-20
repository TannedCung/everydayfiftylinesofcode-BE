from django.contrib.auth.models import User
from django.db import models

class GitHubActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    event_type = models.CharField(max_length=50)
    repo = models.CharField(max_length=255)
    commits = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.event_type}"
