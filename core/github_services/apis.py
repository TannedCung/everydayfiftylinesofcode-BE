# core/github_service.py

import requests

def fetch_github_data(user):
    headers = {"Authorization": f"token {user.social_auth.get().extra_data['access_token']}"}
    # Fetch commit data
    response = requests.get(f"https://api.github.com/users/{user.username}/events", headers=headers)
    # Process response and calculate commits and modifications