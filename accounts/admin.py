"""Este módulo configura o admin para o aplicativo 'accounts'."""
from django.contrib import admin

from accounts import models


class PerfilInLine(admin.StackedInline):
    """Permite que o Perfil seja exibido dentro de CustomUser"""

    model = models.Perfil


class UserAdmin(admin.ModelAdmin):
    """Define como exibir CustomUser."""

    inlines = [PerfilInLine]


admin.site.register(models.CustomUser, UserAdmin)
