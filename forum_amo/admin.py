"""
ADMIN forum_amo
"""
from django.contrib import admin

from forum_amo.models import Duvida, Resposta

admin.site.register(Duvida)
admin.site.register(Resposta)
