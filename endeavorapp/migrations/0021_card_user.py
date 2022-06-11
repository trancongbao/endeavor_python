# Generated by Django 4.0.5 on 2022-08-02 14:17

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('endeavorapp', '0020_deck_order_alter_card_order_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='user',
            field=models.ManyToManyField(through='endeavorapp.UserCard', to=settings.AUTH_USER_MODEL),
        ),
    ]