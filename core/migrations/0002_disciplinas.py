# Generated by Django 3.2.13 on 2022-06-02 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Disciplinas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.TextField()),
                ('descricao', models.TextField()),
                ('cursos', models.ManyToManyField(to='core.Curso')),
            ],
        ),
    ]
