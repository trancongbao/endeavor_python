# Generated by Django 4.0.5 on 2022-08-02 14:25

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('endeavorapp', '0021_card_user'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserCard',
            new_name='StudiedCard',
        ),
    ]
