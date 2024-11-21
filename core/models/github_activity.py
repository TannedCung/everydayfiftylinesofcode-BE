from django.contrib.auth.models import User
from django.db import models

class GitHubEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    event_type = models.CharField(max_length=50)
    repo = models.TextField()  # Changed to TextField for flexibility

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.event_type}"

class GitHubCommit(models.Model):
    github_event = models.ForeignKey(GitHubEvent, on_delete=models.CASCADE)
    sha = models.CharField(unique=True, db_index=True, primary_key=True, max_length=100)
    author = models.JSONField(default=dict)
    message = models.TextField()  # Changed to TextField for long commit messages
    url = models.TextField()  # Changed to TextField for longer URLs

class GithubFileChange(models.Model):
    github_commit = models.ForeignKey(GitHubCommit, on_delete=models.CASCADE)
    sha = models.CharField(unique=True, db_index=True, primary_key=True, max_length=100)
    filename = models.TextField()  # Changed to TextField for flexibility
    status = models.CharField(max_length=50)  # Kept as CharField as it is short
    additions = models.PositiveIntegerField()
    deletions = models.PositiveIntegerField()
    changes = models.PositiveIntegerField()
    blob_url = models.TextField()  # Changed to TextField for longer URLs
    raw_url = models.TextField()  # Changed to TextField for longer URLs
    contents_url = models.TextField()  # Changed to TextField for longer URLs
