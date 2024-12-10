# filters.py
from django_filters import rest_framework as filters
from core.models.challenge import Challenge
from core.models.user_challenge import UserChallenge

class ChallengeFilter(filters.FilterSet):
    my_challenges = filters.BooleanFilter(method='filter_my_challenges', required=False)

    class Meta:
        model = Challenge
        fields = ['my_challenges']

    def filter_my_challenges(self, queryset, name, value):
        if not self.request.user.is_authenticated:
            return queryset
            
        if value is None:  # No filter provided
            return queryset
            
        user_challenge_ids = UserChallenge.objects.filter(
            user=self.request.user
        ).values_list('challenge_id', flat=True)
        
        if value:  # True - show my challenges
            return queryset.filter(id__in=user_challenge_ids)
        else:  # False - show challenges not mine
            return queryset.exclude(id__in=user_challenge_ids)