# Generated by Django 2.0.4 on 2018-08-17 14:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("coup", "0024_auto_20180811_1443"),
    ]

    operations = [
        migrations.AddField(
            model_name="action",
            name="url",
            field=models.CharField(default="actions", max_length=20),
        ),
    ]
