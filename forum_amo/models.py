"""
Models para o app forum_app
"""

from django.db import models
from accounts.models import CustomUser

class Duvida(models.Model):

    """Modelo para dúvidas"""

    titulo = models.CharField(max_length=200)
    descricao = models.TextField(max_length=550)
    autor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return f"Dúvida: {self.titulo}. Descricão: {self.descricao}"
