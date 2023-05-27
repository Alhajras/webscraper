# Generated by Django 4.1 on 2023-05-27 16:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("base", "0028_crawler_max_collected_docs"),
    ]

    operations = [
        migrations.CreateModel(
            name="Action",
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
                ("name", models.CharField(max_length=50)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("click", "Click"),
                            ("wait", "Wait"),
                            ("scroll", "Scroll"),
                        ],
                        default="click",
                        max_length=10,
                    ),
                ),
                ("order", models.PositiveIntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name="ClickAction",
            fields=[
                (
                    "action_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="base.action",
                    ),
                ),
                ("selector", models.TextField()),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("base.action",),
        ),
        migrations.CreateModel(
            name="ScrollAction",
            fields=[
                (
                    "action_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="base.action",
                    ),
                ),
                ("times", models.PositiveIntegerField(default=1)),
                (
                    "direction",
                    models.CharField(
                        choices=[("up", "Up"), ("down", "Down")],
                        default="down",
                        max_length=10,
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("base.action",),
        ),
        migrations.CreateModel(
            name="WaitAction",
            fields=[
                (
                    "action_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="base.action",
                    ),
                ),
                ("time", models.FloatField(default=1)),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("base.action",),
        ),
        migrations.CreateModel(
            name="ActionChain",
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
                (
                    "template",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="base.template"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="action",
            name="action_chain",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="base.actionchain"
            ),
        ),
        migrations.AddField(
            model_name="action",
            name="polymorphic_ctype",
            field=models.ForeignKey(
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="polymorphic_%(app_label)s.%(class)s_set+",
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="action",
            unique_together={("action_chain", "order")},
        ),
    ]