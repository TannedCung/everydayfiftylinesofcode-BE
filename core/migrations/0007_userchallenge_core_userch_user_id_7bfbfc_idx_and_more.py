# Generated by Django 5.0.3 on 2024-12-11 15:36

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_userchallenge_unique_together'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddIndex(
            model_name='userchallenge',
            index=models.Index(fields=['user', 'challenge'], name='core_userch_user_id_7bfbfc_idx'),
        ),
        migrations.AddIndex(
            model_name='userchallenge',
            index=models.Index(fields=['progress'], name='core_userch_progres_3f32c9_idx'),
        ),
    ]
