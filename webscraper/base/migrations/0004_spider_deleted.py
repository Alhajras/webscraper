# Generated by Django 3.2.10 on 2023-01-03 01:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0003_auto_20230103_0102"),
    ]

    operations = [
        migrations.AddField(
            model_name="spider",
            name="deleted",
            field=models.BooleanField(default=False),
        ),
    ]
