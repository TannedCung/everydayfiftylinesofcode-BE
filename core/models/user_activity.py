from django.contrib.auth.models import User
from django.db import models

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    commits = models.IntegerField()
    modifications = models.IntegerField()