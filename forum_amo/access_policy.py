"Arquivo que definem restrições de acesso"
from rest_access_policy import AccessPolicy


class RespostaAccessPolicy(AccessPolicy):
    "Restrições de acesso para o modelo de resposta"
    statements = [
        {
            "action": ["destroy", "partial_update"],
            "principal": "authenticated",
            "effect": "allow",
            "condition": "is_author",
        },
        {
            "action": ["list", "retrieve", "create"],
            "principal": "authenticated",
            "effect": "allow",
        },
    ]

    def is_author(self, request, view, action) -> bool:  # pylint: disable=W0613
        """Função que verifica se asserta que apenas o dono da resposta pode excluí-la"""
        resposta = view.get_object()
        return request.user == resposta.autor


class DuvidaAccessPolicy(AccessPolicy):
    "Restrições de acesso para o modelo de duvidas"
    statements = [
        {
            "action": ["destroy", "partial_update", "correta"],
            "principal": "authenticated",
            "effect": "allow",
            "condition": "is_author",
        },
        {
            "action": ["list", "retrieve", "create", "votar"],
            "principal": "authenticated",
            "effect": "allow",
        },
    ]

    def is_author(self, request, view, action) -> bool:  # pylint: disable=W0613
        """Função que verifica se asserta que apenas o dono da dúvida pode excluí-la"""
        duvida = view.get_object()
        return request.user == duvida.autor
