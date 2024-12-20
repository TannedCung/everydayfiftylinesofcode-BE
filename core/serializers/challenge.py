from rest_framework import serializers 
from drf_spectacular.utils import extend_schema_field
from typing import Optional, Dict
from ..models.challenge import Challenge
from ..models.user_challenge import UserChallenge 
class ChallengeSerializer(serializers.ModelSerializer):
    background_url = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    background_image = serializers.ImageField(required=False, allow_null=True)
    logo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Challenge
        fields = [
            'id', 'name', 'type', 'commitment_by', 'description',
            'target_value', 'frequency', 'start_date', 'end_date',
            'created_at', 'background_image', 'logo',
            'background_url', 'logo_url'
        ]

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_background_url(self, obj: Challenge) -> Optional[str]:
        urls = obj.get_presigned_urls()
        return urls.get('background_url')

    @extend_schema_field(serializers.URLField(allow_null=True)) 
    def get_logo_url(self, obj: Challenge) -> Optional[str]:
        urls = obj.get_presigned_urls()
        return urls.get('logo_url')

    def create(self, validated_data: Dict) -> Challenge:
        instance = super().create(validated_data)
        return instance

    def update(self, instance: Challenge, validated_data: Dict) -> Challenge:
        if 'background_image' in validated_data and instance.background_image:
            instance.background_image.delete(save=False)
        if 'logo' in validated_data and instance.logo:
            instance.logo.delete(save=False)
            
        return super().update(instance, validated_data)

    def validate(self, data):
        """
        Check that end_date is after start_date
        """
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if end_date and start_date and end_date <= start_date:
            raise serializers.ValidationError({
                "end_date": "End date must be at least one day after start date"
            })

        return data

class ChallengeUserSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()
    challenge_progress = serializers.SerializerMethodField()

    class Meta:
        model = UserChallenge
        fields = [
            'user_info',
            'challenge_progress',
            'start_date',
            'highest_streak',
            'progress',
            'progress_detail'
        ]

    def get_user_info(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username
        }

    def get_challenge_progress(self, obj):
        return {
            'start_date': obj.start_date,
            'highest_streak': obj.highest_streak,
            'progress': obj.progress
        }