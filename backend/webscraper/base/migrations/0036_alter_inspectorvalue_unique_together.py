# Generated by Django 4.1 on 2023-06-11 18:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0035_alter_inspectorvalue_unique_together"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="inspectorvalue",
            unique_together=set(),
        ),
    ]
