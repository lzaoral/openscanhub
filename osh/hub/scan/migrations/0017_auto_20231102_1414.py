# Generated by Django 3.2.20 on 2023-11-02 14:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scan', '0016_recompute_subtask_count'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Permissions',
        ),
        migrations.AlterModelOptions(
            name='scan',
            options={'get_latest_by': 'date_submitted', 'permissions': [('errata_xmlrpc_scan', 'Can submit ET scan via XML-RPC')]},
        ),
    ]
