# Generated by Django 4.1.3 on 2024-04-22 17:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0007_alter_perfil_foto"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="emailactivationtoken",
            name="activated_at",
        ),
        migrations.AddField(
            model_name="emailactivationtoken",
            name="expires_at",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 4, 22, 17, 37, 26, 506717, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]