# Generated by Django 4.1.3 on 2023-07-03 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_perfil_entrada"),
    ]

    operations = [
        migrations.AddField(
            model_name="perfil",
            name="foto",
            field=models.ImageField(blank=True, null=True, upload_to=""),
        ),
    ]
