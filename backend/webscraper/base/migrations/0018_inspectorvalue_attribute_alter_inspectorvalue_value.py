# Generated by Django 4.1 on 2023-05-14 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0017_inspector_attribute"),
    ]

    operations = [
        migrations.AddField(
            model_name="inspectorvalue",
            name="attribute",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="inspectorvalue",
            name="value",
            field=models.TextField(blank=True),
        ),
    ]
