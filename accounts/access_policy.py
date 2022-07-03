"""Este módulo contem as definições de aplicativo 'accounts'."""
from rest_access_policy import AccessPolicy


class UserViewAccessPolicy(AccessPolicy):
    """Define o controle de acesso para UserViewSet"""

    statements = [
        {
            "action": ["registrar"],
            "principal": ["anonymous"],
            "effect": "allow",
        },
        {
            "action": ["ativar"],
            "principal": "authenticated",
            "effect": "allow",
        },
    ]
