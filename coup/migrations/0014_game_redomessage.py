# Generated by Django 2.0.4 on 2018-07-29 17:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("coup", "0013_auto_20180729_1322"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="redoMessage",
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
