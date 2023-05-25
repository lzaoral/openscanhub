# Generated by Django 3.2.18 on 2023-05-18 13:30

from django.db import migrations, models

import osh.hub.scan.models


class Migration(migrations.Migration):

    dependencies = [
        ('scan', '0013_alter_profile_command_arguments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='command_arguments',
            field=models.JSONField(default=dict, help_text="this field has to contain key 'analyzers', which is a comma separated list of analyzers, optionally add key csmock_args, which is a string", validators=[osh.hub.scan.models._validate_command_arguments]),
        ),
    ]
