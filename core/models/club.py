from django.contrib.auth.models import User
from django.db import models

class Club(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(User, related_name='clubs')

    def __str__(self):
        return self.name