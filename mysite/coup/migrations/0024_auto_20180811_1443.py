# Generated by Django 2.0.4 on 2018-08-11 18:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('coup', '0023_game_temp_player'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='temp_player',
        ),
        migrations.AddField(
            model_name='game',
            name='player2_turn',
            field=models.BooleanField(default=False),
        ),
    ]
