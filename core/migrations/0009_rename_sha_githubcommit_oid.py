# Generated by Django 5.1.3 on 2024-12-18 12:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_challenge_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='githubcommit',
            old_name='sha',
            new_name='oid',
        ),
    ]
