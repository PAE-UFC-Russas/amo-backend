"""Este módulo configura o admin para o aplicativo 'accounts'."""
from django.contrib import admin

from accounts.models import CustomUser

# Register your models here.
admin.site.register(CustomUser)
