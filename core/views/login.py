# In api/views.py
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.permissions import AllowAny
from django.conf import settings
from allauth.socialaccount.models import SocialAccount, SocialToken

import requests
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['GET'])
@authentication_classes([])  # Disable authentication
@permission_classes([AllowAny])  # Allow all users to access
def github_callback(request):
    """
    Handles GitHub OAuth callback.
    Exchanges code for an access token, retrieves user info, and logs in or creates a user.
    """
    code = request.GET.get("code")
    if not code:
        return Response({"error": "Code is required"}, status=400)

    # Step 1: Exchange code for access token
    token_url = "https://github.com/login/oauth/access_token"
    payload = {
        "client_id": settings.SOCIALACCOUNT_PROVIDERS['github']['APP']['client_id'],
        "client_secret": settings.SOCIALACCOUNT_PROVIDERS['github']['APP']['secret'],
        "code": code,
    }
    headers = {"Accept": "application/json"}

    token_response = requests.post(token_url, data=payload, headers=headers)
    if token_response.status_code != 200:
        return Response({"error": "Failed to fetch access token"}, status=400)

    access_token = token_response.json().get("access_token")
    print(f"[DEBUG]: access_token {access_token}")
    # Step 2: Use the access token to fetch GitHub user info
    user_info_url = "https://api.github.com/user"
    user_info_headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(user_info_url, headers=user_info_headers)

    if user_info_response.status_code != 200:
        print(user_info_response)
        return Response({"error": "Failed to fetch user info"}, status=400)

    user_info = user_info_response.json()
    github_username = user_info.get("login")
    email = user_info.get("email") or f"{github_username}@github.com"

    # Step 3: Check if the user exists, otherwise create one
    user, created = User.objects.get_or_create(username=github_username, defaults={"email": email})

    # Step 4: Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    tokens = {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

    social_account, social_account_created = SocialAccount.objects.get_or_create(
        user=user,
        provider='github',
        defaults={"extra_data": user_info}
    )
    social_token, token_created = SocialToken.objects.get_or_create(
        account=social_account,
        defaults={"token": access_token}
    )

    return Response({
        "message": "Login successful",
        "tokens": tokens,
        "user": {"username": user.username, "email": user.email}
    }, status=200)


@login_required
def user_profile(request):
    user = request.user
    return JsonResponse({
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    })
