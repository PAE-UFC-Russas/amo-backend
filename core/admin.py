"""Este módulo configura o admin para o aplicativo 'core'."""
from django.contrib import admin
from core import models

class CursoFilter(admin.SimpleListFilter):
    title = 'Curso'
    parameter_name = 'curso'

    def lookups(self, request, model_admin):
        return [(curso.id, curso.nome) for curso in models.Curso.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(cursos__id=self.value())
        return queryset

class DisciplinasAdmin(admin.ModelAdmin):
    list_display = ('nome', 'get_cursos')
    search_fields = ('nome',)
    list_filter = (CursoFilter,)

    def get_cursos(self, obj):
        return ", ".join([curso.nome for curso in obj.cursos.all()])
    get_cursos.short_description = 'Cursos'

admin.site.register(models.Curso)
admin.site.register(models.Disciplinas, DisciplinasAdmin)
admin.site.register(models.Agendamento)
admin.site.register(models.Monitoria)