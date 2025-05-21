"""Este módulo configura o admin para o aplicativo 'accounts'."""
from django.contrib import admin

from accounts import models

from django.contrib import admin
from django.contrib.auth.models import Group
from accounts.models import CustomUser, Perfil

class ProfessorFilter(admin.SimpleListFilter):
    """Filtra usuários por tipo de perfil."""

    title = 'professor'
    parameter_name = 'is_professor'

    def lookups(self, request, model_admin):
        return (
            ('1', 'professor'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(groups__name='professor').distinct()
        return queryset


class PerfilInLine(admin.StackedInline):
    """Permite que o Perfil seja exibido dentro de CustomUser"""

    model = models.Perfil


class UserAdmin(admin.ModelAdmin):
    """Define como exibir CustomUser."""

    list_display = ('email', 'username')
    inlines = [PerfilInLine]
    search_fields = ('email', 'perfil__nome_completo')
    list_filter = (ProfessorFilter,)
    


admin.site.register(models.CustomUser, UserAdmin)
