from django.contrib.auth.models import User
from django.db import models

class UserGroup(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='groups')