"""
Model forum_app
"""
from django.db import models

class Duvida(models.Model):

    """Modelo para dúvidas"""

    titulo = models.CharField(max_length=None)
    descricao = models.TextField(max_length=550)
    ESCOLHAS_PRIVACIDADE = ((0, 'Ocultar privacidade'),
                            (1, 'Não ocultar privacidade'),)

    privacidade_autor = PositiveSmallIntegerField(max_length=1, choices=ESCOLHAS_PRIVACIDADE)

    
# Create your models here.
