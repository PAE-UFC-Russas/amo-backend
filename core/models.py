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

DIA_SEMANA = [
    ("0", "Segunda-feira"),
    ("1", "Terça-feira"),
    ("2", "Quarta-feira"),
    ("3", "Quinta-feira"),
    ("4", "Sexta-feira"),
    ("5", "Sábado"),
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
    link_zoom = models.TextField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["data", "disciplina"], name="agendamento_unico"
            )
        ]

    def __str__(self):
        """Representação textual do agendamento"""
        return (
            f"{self.disciplina.nome} - {self.get_solicitante_name()} - "
            f"{self.data.strftime('%d/%m/%Y %H:%M')}"
        )

    def get_solicitante_name(self):
        """Retorna o nome do solicitante ou o e-mail caso não exista perfil."""
        perfil = getattr(self.solicitante, "perfil", None)
        return getattr(perfil, "nome_completo", None) or self.solicitante.email

    def get_data_formatada(self):
        """Retorna a data formatada para exibição"""
        return self.data.strftime("%d/%m/%Y %H:%M")

    get_data_formatada.short_description = "Data"


class Monitoria(models.Model):
    """Page para visualização do monitor, com informações sobre a monitoria."""

    professor = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="monitorias_como_professor",
        null=True,
        blank=True,
    )
    disciplina = models.ForeignKey(
        Disciplinas,
        on_delete=models.CASCADE,
        related_name="DisciplinaMonitorias",
        null=True,
        blank=True,
    )
    monitor = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="Monitorias_como_monitor",
        null=True,
        blank=True,
    )
    dia_semana = models.CharField(
        max_length=1, choices=DIA_SEMANA, null=True, blank=True
    )
    hora_inicio = models.TimeField(blank=True, null=True)
    hora_fim = models.TimeField(blank=True, null=True)
    local = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["monitor", "disciplina", "dia_semana", "hora_inicio"],
                name="horario_unico",
            )
        ]

    def __str__(self):
        return (
            f"{self.get_dia_semana_display()} - {self.hora_inicio} "
            f"às {self.hora_fim} - {self.disciplina.nome}"
        )
