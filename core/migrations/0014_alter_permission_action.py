# Generated by Django 5.1.3 on 2025-01-18 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_challenge_created_by_challenge_updated_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='action',
            field=models.CharField(choices=[('DELETE', 'DELETE'), ('GET', 'GET'), ('EDIT', 'EDIT'), ('CREATE', 'CREATE'), ('MANAGE_ROLES', 'MANAGE_ROLES'), ('MANAGE_MEMBERS', 'MANAGE_MEMBERS')], max_length=20),
        ),
    ]
