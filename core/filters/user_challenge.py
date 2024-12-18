from django_filters import rest_framework as filters
from core.models.user_challenge import UserChallenge

class UserChallengeFilter(filters.FilterSet):
    challenge_id = filters.NumberFilter(field_name='challenge__id')
    
    class Meta:
        model = UserChallenge
        fields = ['challenge_id']