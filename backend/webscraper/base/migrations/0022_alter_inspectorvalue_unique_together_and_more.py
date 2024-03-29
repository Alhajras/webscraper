# Generated by Django 4.1 on 2023-05-14 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0021_alter_inspector_selector"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="inspectorvalue",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="inspectorvalue",
            name="url",
            field=models.URLField(default=""),
        ),
        migrations.AlterUniqueTogether(
            name="inspectorvalue",
            unique_together={("inspector", "runner", "url")},
        ),
    ]
