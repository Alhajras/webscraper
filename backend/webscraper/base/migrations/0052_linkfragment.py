# Generated by Django 4.1 on 2023-07-08 20:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0051_runner_machine"),
    ]

    operations = [
        migrations.CreateModel(
            name="LinkFragment",
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
                ("fragment", models.CharField(max_length=2048)),
                (
                    "parent",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="base.linkfragment",
                    ),
                ),
                (
                    "runner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="base.runner"
                    ),
                ),
            ],
        ),
    ]
