# Generated by Django 4.2.11 on 2024-05-09 02:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0017_alter_emailactivationtoken_expires_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="emailactivationtoken",
            name="expires_at",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 5, 9, 2, 44, 32, 662994, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
