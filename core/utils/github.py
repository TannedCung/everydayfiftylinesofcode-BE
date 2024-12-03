from allauth.socialaccount.models import SocialToken
import requests
from django.utils.timezone import now
from core.models.github_activity import GitHubEvent, GitHubCommit, GithubFileChange
from datetime import datetime, timedelta

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

def initialize_commit_details(start_date, end_date):
    """
    Initialize a dictionary to store commit details for each day between start_date and end_date.

    Args:
        start_date (str): The start date in the format "YYYY-MM-DD".
        end_date (str): The end date in the format "YYYY-MM-DD".

    Returns:
        dict: A dictionary where the keys are dates and the values are empty lists.
    """
    # Convert the input strings to datetime objects
    start_date = datetime.strptime(start_date[:10], "%Y-%m-%d")
    end_date = datetime.strptime(end_date[:10], "%Y-%m-%d")

    commit_details = {}
    current_date = start_date
    while current_date <= end_date:
        commit_details[current_date.strftime("%Y-%m-%d")] = []
        current_date += timedelta(days=1)
    return commit_details

def fetch_commits_with_changes(user, start_date, end_date):
    """
    Fetches the daily commits with changes (additions, deletions) and their details for the user
    using the GitHub GraphQL API. Handles pagination for both repositories and commits.
    """
    token = get_github_access_token(user)
    if not token:
        return {"error": "GitHub token not found for this user."}

    headers = {"Authorization": f"Bearer {token}"}

    # Ensure dates are formatted as ISO-8601 strings with timezone information
    start_date = f"{start_date}T00:00:00Z"
    end_date = f"{end_date}T23:59:59Z"

    # GraphQL query with pagination for repositories and commits
    query = """
    query($username: String!, $start_date: GitTimestamp!, $end_date: GitTimestamp!, $repoCursor: String, $commitCursor: String) {
      user(login: $username) {
        repositories(first: 100, after: $repoCursor) {
          pageInfo {
            endCursor
            hasNextPage
          }
          nodes {
            name
            defaultBranchRef {
              target {
                ... on Commit {
                  history(since: $start_date, until: $end_date, first: 100, after: $commitCursor) {
                    pageInfo {
                      endCursor
                      hasNextPage
                    }
                    edges {
                      node {
                        committedDate
                        additions
                        deletions
                        oid
                        message
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    variables = {
        "username": user.username,
        "start_date": start_date,
        "end_date": end_date,
        "repoCursor": None,
        "commitCursor": None,
    }
    commit_details = initialize_commit_details(start_date, end_date)


    while True:  # Loop for repository pagination
        response = requests.post(
            GITHUB_GRAPHQL_URL, json={"query": query, "variables": variables}, headers=headers
        )

        if response.status_code != 200:
            return {"error": f"Failed to fetch commits. {response.json()}"}

        data = response.json()
        user_data = data.get("data", {}).get("user", {})
        repositories = user_data.get("repositories", {}).get("nodes", [])
        repo_page_info = user_data.get("repositories", {}).get("pageInfo", {})

        # Process each repository
        for repo in repositories:
            if not repo.get("defaultBranchRef"):
                continue

            # Fetch commits with pagination for each repository
            while True:  # Loop for commit pagination within a repository
                history = repo["defaultBranchRef"]["target"].get("history", {})
                for commit in history.get("edges", []):
                    commit_data = commit["node"]
                    commit_date = commit_data["committedDate"][:10]  # Extract YYYY-MM-DD
                    commit_entry = {
                        "oid": commit_data["oid"],
                        "message": commit_data["message"],
                        "additions": commit_data["additions"],
                        "deletions": commit_data["deletions"],
                    }

                    if commit_date not in commit_details:
                        commit_details[commit_date] = []

                    commit_details[commit_date].append(commit_entry)

                # Update commit cursor and check if there's another page
                commit_page_info = history.get("pageInfo", {})
                if commit_page_info.get("hasNextPage"):
                    variables["commitCursor"] = commit_page_info["endCursor"]
                else:
                    variables["commitCursor"] = None
                    break

        # Update repository cursor and check if there's another page
        if repo_page_info.get("hasNextPage"):
            variables["repoCursor"] = repo_page_info["endCursor"]
        else:
            break

    return commit_details

def get_github_access_token(user):
    try:
        token = SocialToken.objects.get(account__user=user, account__provider="github")
        return token.token
    except SocialToken.DoesNotExist:
        return None


def fetch_github_commit_change(commit, headers):
    """
    Fetches details of a specific commit including file changes.
    """
    url = commit["url"]
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
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    url = f"https://api.github.com/users/{user.username}/events?per_page=100"
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
            repo=repo_name,
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
                    "url": url,
                },
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
                        },
                    )
            except Exception as e:
                print(e)

            synced_commits.append(commit_instance.sha)

    return {"synced_commits": synced_commits}


def fetch_contribution_calendar(user, year=None):
    """
    Fetches the contribution calendar for the user using the GitHub GraphQL API.
    An optional `year` parameter can be passed to filter contributions for a specific year.
    """
    token = get_github_access_token(user)
    if not token:
        return {"error": "GitHub token not found for this user."}

    headers = {"Authorization": f"Bearer {token}"}

    # Default to the current year if no year is provided
    if year is None:
        year = now().year

    # Build start and end dates for the year in the correct string format
    start_date = f"{year}-01-01T00:00:00Z"
    end_date = f"{year}-12-31T23:59:59Z"

    # GraphQL query to fetch the contribution calendar
    query = """
    query($username: String!, $start_date: DateTime!, $end_date: DateTime!) {
      user(login: $username) {
        contributionsCollection(from: $start_date, to: $end_date) {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """
    variables = {"username": user.username, "start_date": start_date, "end_date": end_date}

    response = requests.post(
        GITHUB_GRAPHQL_URL, json={"query": query, "variables": variables}, headers=headers
    )

    if response.status_code == 200:
        return response.json()
    return {"error": "Failed to fetch contribution calendar."}

def calculate_activity_streak(contribution_calendar, daily_goal, today=None):
    """
    Calculates the current and longest streak from the contribution calendar.
    today: int: The number of the day today
    """
    contributions = [
        day["contributionCount"]
        for week in contribution_calendar["weeks"]
        for day in week["contributionDays"]
    ]
    streak = 0
    max_streak = 0
    for idx, count in enumerate(contributions):
        if today and idx + 1 >= today:
            break
        if count >= daily_goal:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    return {"current_streak": streak, "longest_streak": max_streak}


def calculate_daily_goal_progress(contribution_calendar, daily_goal):
    """
    Calculates the progress toward the daily goal.
    """
    today = datetime.now().date()
    today_contributions = next(
        (
            day["contributionCount"]
            for week in contribution_calendar["weeks"]
            for day in week["contributionDays"]
            if datetime.strptime(day["date"], "%Y-%m-%d").date() == today
        ),
        0,
    )
    progress = min(today_contributions / daily_goal, 1.0) * 100
    return {"progress": progress, "daily_goal": daily_goal, "today": today_contributions}
