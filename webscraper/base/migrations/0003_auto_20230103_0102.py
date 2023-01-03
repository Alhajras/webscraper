# Generated by Django 3.2.10 on 2023-01-03 01:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_alter_spider_completed_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spider',
            name='completed_at',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='spider',
            name='url',
            field=models.TextField(),
        ),
    ]
