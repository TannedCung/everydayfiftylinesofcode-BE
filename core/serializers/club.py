# core/serializers/club.py
from rest_framework import serializers
from core.models.club import Club
from django.contrib.auth.models import User

class ClubSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    class Meta:
        model = Club
        fields = ['id', 'name', 'description', 'members']