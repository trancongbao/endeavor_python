# Generated by Django 4.0.5 on 2022-07-31 04:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('endeavorapp', '0009_rename_dict_entry_wordincard_word'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='order',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='wordincard',
            name='display_order',
            field=models.PositiveSmallIntegerField(),
        ),
    ]
