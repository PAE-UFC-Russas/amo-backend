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

        Por padrão filtra a lista de agendamentos para que o usuário atual tenha acesso
        apenas a seus agendamentos. Porém quando a busca é filtrada por disciplina, e o
        usuário é monitor, verificamos se é monitor da disciplina atual."""
        if disciplina_id := request.query_params.get("disciplina", None):
            if (
                request.user.groups.filter(name__in=["monitor"]).exists()
                and models.Disciplinas.objects.filter(
                    pk=disciplina_id, monitores=request.user
                ).exists()
            ):
                return qs

        return qs.filter(solicitante=request.user)
