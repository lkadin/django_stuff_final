# Generated by Django 2.0.4 on 2018-07-23 18:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("coup", "0004_delete_actionhistory"),
    ]

    operations = [
        migrations.CreateModel(
            name="ActionHistory",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(default="Assassinate", max_length=20)),
                ("tran_date", models.DateTimeField(auto_now_add=True)),
                ("player1", models.CharField(default="Lee", max_length=20)),
                ("player2", models.CharField(default="Lee", max_length=20)),
            ],
        ),
    ]
