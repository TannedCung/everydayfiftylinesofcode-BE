# Generated by Django 5.1.3 on 2024-12-11 15:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_userchallenge_core_userch_user_id_7bfbfc_idx_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='challenge',
            options={'ordering': ['name']},
        ),
    ]