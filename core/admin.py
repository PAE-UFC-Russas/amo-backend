"""Este módulo configura o admin para o aplicativo 'core'."""
from django.contrib import admin

from core.models import Curso, Disciplinas

admin.site.register(Curso)
admin.site.register(Disciplinas)
