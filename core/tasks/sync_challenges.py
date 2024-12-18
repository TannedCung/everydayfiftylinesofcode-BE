# core/tasks/tasks.py
from celery import shared_task
from core.models.user_challenge import UserChallenge
from django.contrib.auth.models import User

@shared_task
def update_user_challenges(user_id, *args, **kwargs):
    """
    Update user's challenges based on contribution data
    """
    try:
        user = User.objects.get(id=user_id)
        active_challenges = UserChallenge.objects.filter(
            user=user
        )

        for user_challenge in active_challenges:
            user_challenge.update_progress()
            
        return {
            "status": "success",
            "message": f"Updated {active_challenges.count()} challenges"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }