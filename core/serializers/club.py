# core/serializers/club.py
from rest_framework import serializers
from core.models.club import Club
from django.contrib.auth.models import User

class ClubSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    background_image = serializers.ImageField(required=False, allow_null=True)
    avatar = serializers.ImageField(required=False, allow_null=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)


    class Meta:
        model = Club
        fields = ['id', 'name', 'description', 'members', 'background_image', 'avatar']
        read_only_fields = ['created_by']