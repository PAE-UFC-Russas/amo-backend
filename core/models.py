"""Este módulo define os modelos do aplicativo 'core'."""
import uuid

from django.db import models


class CreateModificationMixin(models.Model):
    """Classe base para salvar data e hora de criação/modificação"""

    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


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


class Arquivo(CreateModificationMixin, models.Model):
    """Representação de um arquivo, possibilita relacionamento entre outros modelos e arquivos."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField()
