# Generated by Django 5.1.3 on 2024-12-23 17:38

import core.models.club
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_rename_sha_githubcommit_oid'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('background_image', models.ImageField(blank=True, null=True, storage=core.models.club.MinioStorage(), upload_to=core.models.club.club_image_path)),
                ('avatar', models.ImageField(blank=True, null=True, storage=core.models.club.MinioStorage(), upload_to=core.models.club.club_image_path)),
                ('members', models.ManyToManyField(related_name='clubs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
