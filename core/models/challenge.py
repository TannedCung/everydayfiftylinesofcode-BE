from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class MinioStorage(S3Boto3Storage):
    location = 'challenges'
    default_acl = 'private'

def challenge_image_path(instance, filename):
    return f'challenges/{instance.id}/{filename}'

storage = MinioStorage()

class Challenge(models.Model):
    TYPE_CHOICES = [
        ('commits', 'Commits'),
        ('lines_of_code', 'Lines of Code'),
    ]

    COMMITMENT_CHOICES = [
        ('daily', 'Daily'),
        ('accumulate', 'Accumulate'),
    ]

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    commitment_by = models.CharField(max_length=20, choices=COMMITMENT_CHOICES)
    description = models.TextField()
    target_value = models.PositiveIntegerField(default=0)
    frequency = models.PositiveIntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # New fields
    background_image = models.ImageField(
        upload_to=challenge_image_path,
        storage=MinioStorage(),
        null=True,
        blank=True
    )
    logo = models.ImageField(
        upload_to=challenge_image_path,
        storage=MinioStorage(),
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['name'] 

    def __str__(self):
        return f"{self.name}"

    def get_presigned_urls(self):
        """Generate presigned URLs with 1 hour expiration"""
        urls = {}
        
        if self.background_image:
            urls['background_url'] = storage.url(
                self.background_image.name,
                # parameters={'ExpiresIn': 3600}
            )
        
        if self.logo:
            urls['logo_url'] = storage.url(
                self.logo.name,
                # parameters={'ExpiresIn': 3600}
            )
            
        return urls