# Generated by Django 2.0.4 on 2018-09-14 13:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('coup', '0034_auto_20180907_1652'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='discards',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='second_player',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
