from allauth.socialaccount.models import SocialToken
import requests

def get_github_access_token(user):
    try:
        token = SocialToken.objects.get(account__user=user, account__provider='github')
        return token.token
    except SocialToken.DoesNotExist:
        return None

def fetch_github_commits(user):
    token = get_github_access_token(user)
    if not token:
        return {"error": "GitHub token not found for this user."}

    # Make a request to the GitHub API
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    url = f'https://api.github.com/users/{user.username}/events'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        events = response.json()
        # Filter PushEvents (commits)
        push_events = [event for event in events if event["type"] == "PushEvent"]
        commits = []
        for event in push_events:
            repo_name = event["repo"]["name"]
            for commit in event["payload"]["commits"]:
                commits.append({
                    "repo": repo_name,
                    "message": commit["message"],
                    "url": commit["url"]
                })
        return commits
    else:
        return {"error": f"GitHub API returned status {response.status_code}"}