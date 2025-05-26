from django.contrib import admin
from core import models

@admin.register(models.Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('mostrar_agendamento', 'status', 'get_data_formatada')

    def mostrar_agendamento(self, obj):
        return f"{obj.disciplina.nome} - {obj.get_solicitante_name()} - {obj.get_data_formatada()}"
    mostrar_agendamento.short_description = 'Agendamento'

admin.site.register(models.Curso)
admin.site.register(models.Disciplinas)
admin.site.register(models.Monitoria)
 