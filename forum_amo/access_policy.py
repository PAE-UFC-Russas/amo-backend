"Arquivo que definem restrições de acesso"
from rest_access_policy import AccessPolicy


class RespostaAccessPolicy(AccessPolicy):
    "Restrições de acesso para o modelo de resposta"
    statements = [
        {
            "action": ["destroy", "partial_update"],
            "principal": "authenticated",
            "effect": "allow",
            "condition": "has_perm",
        },
        {
            "action": ["list", "retrieve", "create"],
            "principal": "authenticated",
            "effect": "allow",
        },
    ]

    def has_perm(self, request, view, action) -> bool:  # pylint: disable=W0613
        """Função que verifica se asserta que apenas o dono da resposta,
        monitor ou professor pode excluí-la"""
        resposta = view.get_object()
        return (
            request.user == resposta.autor
            or request.user.groups.filter(name="monitor").exists()
            or request.user.groups.filter(name="professor").exists()
        )


class DuvidaAccessPolicy(AccessPolicy):
    "Restrições de acesso para o modelo de duvidas"
    statements = [
        {
            "action": ["destroy", "partial_update", "correta"],
            "principal": "authenticated",
            "effect": "allow",
            "condition": "has_perm",
        },
        {
            "action": ["list", "retrieve", "create", "votar"],
            "principal": "authenticated",
            "effect": "allow",
        },
    ]

    def has_perm(self, request, view, action) -> bool:  # pylint: disable=W0613
        """Função que verifica se asserta que apenas o dono da dúvida,
        monitor ou professor pode excluí-la"""
        duvida = view.get_object()
        return (
            request.user == duvida.autor
            or request.user.groups.filter(name="monitor").exists()
            or request.user.groups.filter(name="professor").exists()
        )
