"""
Models para o app forum_app
"""

from django.db import models

class Duvida(models.Model):

    """Modelo para dúvidas"""

    titulo = models.CharField(max_length=200)
    descricao = models.TextField(max_length=550)
    privacidade_autor = models.BooleanField(default=True)


    
# Create your models here.
