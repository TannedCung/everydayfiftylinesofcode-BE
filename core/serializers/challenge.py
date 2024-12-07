from rest_framework import serializers 
from drf_spectacular.utils import extend_schema_field
from typing import Optional, Dict
from ..models.challenge import Challenge

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