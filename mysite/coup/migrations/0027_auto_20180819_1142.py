# Generated by Django 2.0.4 on 2018-08-19 15:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('coup', '0026_action_pending_required'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionhistory',
            name='player2',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
