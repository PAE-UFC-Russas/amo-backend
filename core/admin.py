"""Este módulo configura o admin para o aplicativo 'core'."""
from django.contrib import admin

from core.models import Arquivo, Curso, Disciplinas

admin.site.register(Curso)
admin.site.register(Disciplinas)
admin.site.register(Arquivo)

