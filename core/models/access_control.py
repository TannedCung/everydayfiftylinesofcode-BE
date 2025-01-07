from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from ..constants import Roles, Actions

class Role(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[(r.value, r.value) for r in Roles])
    
    # Generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        unique_together = ['user', 'content_type', 'object_id']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

class Permission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    action = models.CharField(max_length=20, choices=[(a.value, a.value) for a in Actions])

    class Meta:
        unique_together = ['role', 'action']