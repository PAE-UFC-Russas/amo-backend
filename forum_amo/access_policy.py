"Arquivo que definem restrições de acesso"
from rest_access_policy import AccessPolicy


class RespostaAccessPolicy(AccessPolicy):
    "Restrições de acesso para o modelo de resposta"
    statements = [
        {
            "action": ["list", "retrieve", "create"],
            "principal": "authenticated",
            "effect": "allow",
        }
    ]
