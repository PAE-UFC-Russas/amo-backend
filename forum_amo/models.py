"""
Models para o app forum_app
"""

from django.db import models

from accounts.models import CustomUser
from core.models import Disciplinas


class Duvida(models.Model):

    """Modelo para dúvidas"""

    titulo = models.CharField(max_length=200)
    descricao = models.TextField(max_length=550)
    data = models.DateTimeField(auto_now=True)
    disciplina = models.ForeignKey(Disciplinas, on_delete=models.CASCADE)
    #Ao usuário criar a dúvida, ainda não haverá respostas, assim não é possivel adicionar uma resposta_correta.
    #Por isso está como blank=True
    resposta_correta = models.ForeignKey(
        "Resposta", on_delete=models.SET_NULL, null=True, blank=True related_name="+"
    )
    autor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
    votos = models.IntegerField(default=0)

    def __str__(self):
        return f"Dúvida: {self.titulo}. Descricão: {self.descricao}"


class Resposta(models.Model):
    """Modelo para respostas às dúvidas"""

    autor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    duvida = models.ForeignKey(Duvida, on_delete=models.CASCADE)
    resposta = models.TextField(max_length=750)
    data = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dúvida_id: {self.duvida}.Data: {self.data} Autor_id: {self.autor}"


class VotoDuvida(models.Model):
    "Modelo para usuários poderem votar nas dúvidas"
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    duvida = models.ForeignKey(Duvida, on_delete=models.CASCADE)
    data_criada = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["usuario", "duvida"], name="voto_unico")
        ]
