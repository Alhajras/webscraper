# Generated by Django 4.1 on 2023-05-29 17:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0033_alter_action_options_alter_action_unique_together"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="inspectorvalue",
            unique_together={("value", "inspector", "runner", "url")},
        ),
    ]
