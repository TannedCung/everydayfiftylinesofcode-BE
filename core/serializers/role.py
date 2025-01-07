from rest_framework import serializers
from django.contrib.auth.models import User
from ..constants import Roles

class RoleAssignmentSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    role = serializers.ChoiceField(choices=[(r.value, r.value) for r in Roles])