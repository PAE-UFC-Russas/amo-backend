"""Este módulo contem as definições de aplicativo 'core'."""
from rest_access_policy import AccessPolicy

from core import models


class CursoAccessPolicy(AccessPolicy):
    """Define o controle de acesso para CursoViewSet"""

    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": "authenticated",
            "effect": "allow",
        },
        {
            "action": ["list", "retrieve", "create", "partial_update", "destroy"],
            "principal": ["admin"],
            "effect": "allow",
        },
    ]


class DisciplinaAccessPolicy(AccessPolicy):
    """Define o controle de acesso para DisciplinaViewSet"""

    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": "authenticated",
            "effect": "allow",
        },
        {
            "action": ["list", "retrieve", "create", "partial_update", "destroy"],
            "principal": ["admin"],
            "effect": "allow",
        },
    ]


class AgendamentoAccessPolicy(AccessPolicy):
    """Controle de acesso para as views de agendamentos."""

    statements = [
        {
            "action": ["list", "retrieve", "create"],
            "principal": "authenticated",
            "effect": "allow",
        },
        {
            "action": ["update", "partial_update"],
            "principal": "authenticated",
            "effect": "allow",
            "condition_expression": ["(is_monitor or is_solicitante)"],
        },
    ]

    def is_solicitante(self, request, view, action):  # pylint: disable=unused-argument
        """Verifica se o usuário é o solicitante do agendamento."""
        agendamento = view.get_object()
        return request.user == agendamento.solicitante

    def is_monitor(self, request, view, action):  # pylint: disable=unused-argument
        """Verifica se o usuário atual é monitor da disciplina."""
        return models.Disciplinas.objects.filter(monitores=request.user).exists()

    @classmethod
    def scope_queryset(cls, request, qs):
        """Filtra os resultados para controlar o acesso aos agendamentos.

        - Alunos tem acesso apenas a seus agendamentos.
        - Monitores tem acesso a todos os agendamentos das disciplinas que são monitores.
        - Professores podem ver todos os agendamentos de todas as disciplinas."""

        if (
            request.user.groups.filter(name__in=["monitor"]).exists()
            and models.Disciplinas.objects.filter(monitores=request.user).exists()
        ):

            user = request.user
            disciplinas = models.Disciplinas.objects.filter(monitores=user)
            new_qs = models.Agendamento.objects.filter(disciplina__id__in=disciplinas)

            return new_qs
        if request.user.groups.filter(name__in=["professor"]).exists():
            user = request.user
            disciplinas = models.Disciplinas.objects.filter(professores=user)
            new_qs = models.Agendamento.objects.filter(disciplina__id__in=disciplinas)

            return qs

        return qs.filter(solicitante=request.user)
