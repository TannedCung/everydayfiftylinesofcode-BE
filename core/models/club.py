# core/models/club.py
from django.contrib.auth.models import User
from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage

class MinioStorage(S3Boto3Storage):
    location = 'clubs'
    default_acl = 'private'

def club_image_path(instance, filename):
    return f'clubs/{instance.id}/{filename}'

storage = MinioStorage()

class Club(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(User, related_name='clubs')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_clubs')
    background_image = models.ImageField(upload_to=club_image_path, storage=storage, null=True, blank=True)
    avatar = models.ImageField(upload_to=club_image_path, storage=storage, null=True, blank=True)

    def __str__(self):
        return self.name