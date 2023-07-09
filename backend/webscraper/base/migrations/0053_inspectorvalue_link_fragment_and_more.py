# Generated by Django 4.1 on 2023-07-09 11:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0052_linkfragment"),
    ]

    operations = [
        migrations.AddField(
            model_name="inspectorvalue",
            name="link_fragment",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="base.linkfragment",
            ),
        ),
        migrations.AlterField(
            model_name="linkfragment",
            name="fragment",
            field=models.CharField(max_length=100),
        ),
    ]
