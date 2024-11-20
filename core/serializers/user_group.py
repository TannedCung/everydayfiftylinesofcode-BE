from rest_framework import serializers
from core.models.user_group import UserGroup

class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = ["name", "members"]