# core/tasks/github_tasks.py
from celery import shared_task
from core.models.github_activity import GitHubEvent, GitHubCommit, GithubFileChange
from django.contrib.auth.models import User
from datetime import datetime

@shared_task
def update_github_commits(user_id, commit_data):
    """
    Update GitHub commits in database from API data
    """
    try:
        user = User.objects.get(id=user_id)
        
        for date, commits in commit_data.items():
            # Skip empty days
            if not commits:
                continue
                
            for commit in commits:
                # Create or update GitHubEvent
                event, _ = GitHubEvent.objects.get_or_create(
                    user=user,
                    date=datetime.fromisoformat(date).date(),
                    defaults={'event_type': 'commit'}
                )
                
                # Create or update GitHubCommit
                GitHubCommit.objects.update_or_create(
                    oid=commit['oid'],
                    defaults={
                        'github_event': event,
                        'message': commit['message'],
                        'additions': commit.get('additions', 0),
                        'deletions': commit.get('deletions', 0),
                        'date': datetime.fromisoformat(date).date()
                    }
                )
        
        return {
            'status': 'success',
            'message': f'Updated commits for user {user.username}'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }
