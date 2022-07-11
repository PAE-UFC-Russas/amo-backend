"""
Model forum_app
"""
from django.db import models

class Duvida(models.Model):

    """Modelo para dúvidas"""

    titulo = models.CharField(required=True, max_lenght=None)
    descricao = models.TextField(required=True, max_lenght=550)
    ESCOLHAS_PRIVACIDADE = ((0, 'Ocultar privacidade'),
                            (1, 'Não ocultar privacidade'),)

    privacidade_autor = PositiveSmallIntegerField(required=True, max_lenght=1, choices=ESCOLHAS_PRIVACIDADE)

    
# Create your models here.
