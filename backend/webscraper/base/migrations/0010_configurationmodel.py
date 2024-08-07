# Generated by Django 4.1 on 2023-03-16 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0009_auto_20230108_0021"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConfigurationModel",
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
                ("max_num_crawlers", models.PositiveSmallIntegerField(default=2)),
                ("max_num_machines", models.PositiveSmallIntegerField(default=2)),
                ("min_sleep_time", models.FloatField(default=0.25)),
            ],
            options={
                "verbose_name": "Site Configuration",
            },
        ),
    ]
