# Generated by Django 4.1 on 2023-07-15 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0061_alter_inspector_variable_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="inspector",
            name="clean_up_expression",
            field=models.TextField(blank=True, default=""),
        ),
    ]
