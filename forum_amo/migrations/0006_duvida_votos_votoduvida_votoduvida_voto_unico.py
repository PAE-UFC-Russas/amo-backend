# Generated by Django 4.1.1 on 2022-09-23 20:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("forum_amo", "0005_duvida_resposta_correta"),
    ]

    operations = [
        migrations.AddField(
            model_name="duvida",
            name="votos",
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name="VotoDuvida",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("data_criada", models.DateTimeField(auto_now_add=True)),
                (
                    "duvida",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="forum_amo.duvida",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="votoduvida",
            constraint=models.UniqueConstraint(
                fields=("usuario", "duvida"), name="voto_unico"
            ),
        ),
    ]
