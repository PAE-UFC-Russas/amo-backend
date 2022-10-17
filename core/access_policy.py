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
