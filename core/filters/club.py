from django_filters import rest_framework as filters
from core.models.club import Club

class ClubFilter(filters.FilterSet):
    my_clubs = filters.BooleanFilter(method='filter_my_clubs', required=False)

    class Meta:
        model = Club
        fields = ['my_clubs']

    def filter_my_clubs(self, queryset, name, value):
        if not self.request.user.is_authenticated:
            return queryset
            
        if value is None:  # No filter provided
            return queryset
            
        if value:  # True - show my clubs
            return queryset.filter(members=self.request.user)
        else:  # False - show clubs I'm not in
            return queryset.exclude(members=self.request.user)