from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def get_github_profile(request):
    # Get the currently authenticated user
    user = request.user
    try:
        social_account = SocialAccount.objects.get(user=user, provider='github')
        github_profile = social_account.extra_data  # Contains GitHub profile info
        return Response(github_profile)
    except SocialAccount.DoesNotExist:
        return Response({"error": "GitHub account not linked"}, status=400)
