# Generated by Django 4.1 on 2023-07-02 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0049_crawler_show_browser"),
    ]

    operations = [
        migrations.AddField(
            model_name="actionchain",
            name="disabled",
            field=models.BooleanField(default=True),
        ),
    ]
