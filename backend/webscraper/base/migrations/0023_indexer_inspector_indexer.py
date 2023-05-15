# Generated by Django 4.1 on 2023-05-15 15:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0022_alter_inspectorvalue_unique_together_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Indexer",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("deleted", models.BooleanField(default=False)),
                ("name", models.CharField(max_length=50, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Running", "Running"),
                            ("Completed", "Completed"),
                            ("Exit", "Exit"),
                        ],
                        default="Running",
                        max_length=10,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="inspector",
            name="indexer",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="base.indexer",
            ),
        ),
    ]