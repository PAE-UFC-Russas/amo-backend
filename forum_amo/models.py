"""
Models para o app forum_app
"""

from django.db import models

ESCOLHAS_PRIVACIDADE = ((0, 'Ocultar privacidade'),
                           (1, 'Não ocultar privacidade'),)


class Duvida(models.Model):

    """Modelo para dúvidas"""

    titulo = models.CharField(max_length=200)
    descricao = models.TextField(max_length=550)
    privacidade_autor = models.PositiveSmallIntegerField(choices=ESCOLHAS_PRIVACIDADE)

    
# Create your models here.
