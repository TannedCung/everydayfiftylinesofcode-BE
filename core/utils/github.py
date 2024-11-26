from allauth.socialaccount.models import SocialToken
import requests
from core.models.github_activity import GitHubEvent, GitHubCommit, GithubFileChange

def get_github_access_token(user):
    try:
        token = SocialToken.objects.get(account__user=user, account__provider='github')
        return token.token
    except SocialToken.DoesNotExist:
        return None

def fetch_github_commit_change(commit, headers):
    """
    Fetches details of a specific commit including file changes.
    """
    url = commit['url']
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Returns commit details
    return None

def fetch_github_commits(user):
    """
    Fetches GitHub events, filters push events, and syncs commits and file changes.
    """
    token = get_github_access_token(user)
    if not token:
        return {"error": "GitHub token not found for this user."}

    # Make a request to the GitHub API
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    url = f'https://api.github.com/users/{user.username}/events?per_page=100'
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"error": f"GitHub API returned status {response.status_code}"}

    events = response.json()

    # Filter PushEvents (commits)
    push_events = [event for event in events if event["type"] == "PushEvent"]
    synced_commits = []

    for event in push_events:
        # Create or get the GitHub event in the database
        repo_name = event["repo"]["name"]
        event_instance, _ = GitHubEvent.objects.get_or_create(
            user=user,
            date=event["created_at"].split("T")[0],
            event_type=event["type"],
            repo=repo_name
        )

        # Process each commit in the event
        for commit_data in event["payload"]["commits"]:
            sha = commit_data["sha"]
            message = commit_data["message"]
            url = commit_data["url"]
            author_data = commit_data.get("author", {})

            # Fetch full commit details
            commit_details = fetch_github_commit_change(commit_data, headers)
            if not commit_details:
                continue  # Skip if commit details could not be fetched

            # Create or get the GitHub commit in the database
            commit_instance, _ = GitHubCommit.objects.get_or_create(
                github_event=event_instance,
                sha=sha,
                defaults={
                    "author": author_data,
                    "committer": commit_details.get("commit", {}).get("committer", {}),
                    "date": commit_details.get("commit", {}).get("committer", {}).get("date", "").split("T")[0],
                    "additions": commit_details.get("stats", {}).get("additions", 0),
                    "deletions": commit_details.get("stats", {}).get("deletions", 0),
                    "changes": commit_details.get("stats", {}).get("total", 0),
                    "message": message,
                    "url": url
                }
            )

            # Process file changes for the commit
            files = commit_details.get("files", [])
            try:
                for file in files:
                    GithubFileChange.objects.get_or_create(
                        github_commit=commit_instance,
                        sha=file.get("sha"),
                        defaults={
                            "filename": file.get("filename"),
                            "status": file.get("status"),
                            "additions": file.get("additions", 0),
                            "deletions": file.get("deletions", 0),
                            "changes": file.get("changes", 0),
                            "blob_url": file.get("blob_url"),
                            "raw_url": file.get("raw_url"),
                            "contents_url": file.get("contents_url"),
                        }
                    )
            except Exception as e:
                print(e)

            synced_commits.append(commit_instance.sha)

    return {"synced_commits": synced_commits}
