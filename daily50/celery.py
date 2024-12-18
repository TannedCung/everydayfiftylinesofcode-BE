from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daily50.settings')

app = Celery('daily50')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()