# Generated by Django 4.1 on 2023-03-16 19:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0010_configurationmodel"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Spider",
            new_name="Crawler",
        ),
        migrations.RenameField(
            model_name="runner",
            old_name="spider",
            new_name="crawler",
        ),
    ]