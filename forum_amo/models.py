"""
Models para o app forum_app
"""

from django.db import models

from accounts.models import CustomUser


class Duvida(models.Model):

    """Modelo para dúvidas"""

    titulo = models.CharField(max_length=200)
    descricao = models.TextField(max_length=550)

    def __str__(self):
        return f"Dúvida: {self.titulo}. Descricão: {self.descricao}"


class Resposta(models.Model):
    """Modelo para respostas às dúvidas"""

    autor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    duvida_id = models.ForeignKey(Duvida, on_delete=models.CASCADE)
    resposta = models.TextField(max_length=750)
    data_criada = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dúvida_id: {self.duvida_id}.Data: {self.data_criada} Autor_id: {self.autor}"
