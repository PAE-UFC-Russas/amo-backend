"""Este módulo define os modelos do aplicativo 'core'."""
from django.db import models


class Curso(models.Model):
    """Representação de um curso."""

    nome = models.TextField()
    descricao = models.TextField()

    def __str__(self):
        return f"Curso: {self.nome}"


class Disciplinas(models.Model):
    """Representação de uma disciplina."""

    nome = models.TextField()
    descricao = models.TextField()

    cursos = models.ManyToManyField(Curso)
    monitores = models.ManyToManyField(
        "accounts.CustomUser", related_name="monitoria", blank=True
    )
    professores = models.ManyToManyField(
        "accounts.CustomUser", related_name="disciplinas", blank=True
    )

    def __str__(self):
        return f"Disciplina: {self.nome}"
