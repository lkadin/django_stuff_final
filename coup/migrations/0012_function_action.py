# Generated by Django 2.0.4 on 2018-07-28 23:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("coup", "0011_function"),
    ]

    operations = [
        migrations.AddField(
            model_name="function",
            name="action",
            field=models.ForeignKey(
                default=0, on_delete=django.db.models.deletion.CASCADE, to="coup.Action"
            ),
        ),
    ]
