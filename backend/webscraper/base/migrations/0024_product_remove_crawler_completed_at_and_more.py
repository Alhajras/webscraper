# Generated by Django 4.1 on 2023-05-21 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0023_indexer_inspector_indexer"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("data", models.JSONField()),
            ],
        ),
        migrations.RemoveField(
            model_name="crawler",
            name="completed_at",
        ),
        migrations.AlterField(
            model_name="indexer",
            name="status",
            field=models.CharField(
                choices=[
                    ("New", "New"),
                    ("Running", "Running"),
                    ("Completed", "Completed"),
                    ("Exit", "Exit"),
                ],
                default="New",
                max_length=10,
            ),
        ),
    ]
