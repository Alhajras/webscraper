# Generated by Django 3.2.10 on 2023-01-07 00:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0006_alter_spider_completed_at"),
    ]

    operations = [
        migrations.CreateModel(
            name="Template",
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
                ("name", models.CharField(max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("deleted", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ("created_at",),
            },
        ),
        migrations.CreateModel(
            name="Inspetor",
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
                ("name", models.CharField(max_length=100)),
                ("selector", models.CharField(max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("deleted", models.BooleanField(default=False)),
                (
                    "template",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="base.template"
                    ),
                ),
            ],
            options={
                "ordering": ("created_at",),
            },
        ),
        migrations.AddField(
            model_name="spider",
            name="template",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="templates",
                to="base.template",
            ),
        ),
    ]
