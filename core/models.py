"""Este módulo define os modelos do aplicativo 'core'."""
from django.db import models

TIPOS_AGENDAMENTO = [
    ("presencial", "Presencial"),
    ("virtual", "Virtual"),
]

STATUS_AGENDAMENTO = [
    ("confirmado", "Confirmado"),
    ("aguardando", "Aguardando Confirmação"),
    ("cancelado", "Cancelado"),
]


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


class Agendamento(models.Model):
    """Representa um adentamento para atendimento."""

    disciplina = models.ForeignKey(Disciplinas, on_delete=models.CASCADE)
    solicitante = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPOS_AGENDAMENTO)
    status = models.CharField(
        max_length=10, choices=STATUS_AGENDAMENTO, default="aguardando"
    )
    data = models.DateTimeField()
    assunto = models.TextField()
    descricao = models.TextField()
