# Generated by Django 3.2.10 on 2023-01-03 23:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0005_spider_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="spider",
            name="completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]