# Generated by Django 4.2.11 on 2024-04-28 23:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0013_alter_emailactivationtoken_expires_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="emailactivationtoken",
            name="expires_at",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 4, 29, 0, 10, 42, 923560, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
