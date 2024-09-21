"""Este módulo configura o admin para o aplicativo 'core'."""
from django.contrib import admin

from core import models

admin.site.register(models.Curso)
admin.site.register(models.Disciplinas)
admin.site.register(models.Agendamento)
admin.site.register(models.Monitoria)

