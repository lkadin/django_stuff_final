# Generated by Django 2.0.4 on 2018-08-08 15:29

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("coup", "0018_auto_20180808_1113"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="game",
            name="discardRequired",
        ),
        migrations.RemoveField(
            model_name="game",
            name="redoMessage",
        ),
    ]
