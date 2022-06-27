from rest_access_policy import AccessPolicy


class CursoAccessPolicy(AccessPolicy):
    """Define o controle de acesso para CursoViewSet"""

    statements = [
        {
            "action": ["list"],
            "principal": "authenticated",
            "effect": "allow",
        },
        {
            "action": ["retrieve", "create", "partial_update", "destroy"],
            "principal": ["admin"],
            "effect": "allow",
        },
    ]
