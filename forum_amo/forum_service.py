"""Este módulo contem ações de gerenciamento do fórum."""
from accounts import account_management_service
from forum_amo import models


def get_resposta(pk: int) -> dict:
    """Retorna uma Resposta"""
    resposta_model = models.Resposta.objects.get(pk=pk)

    resposta_dict = {
        "id": resposta_model.id,
        "duvida": resposta_model.duvida_id,
        "data": resposta_model.data.astimezone(),
        "resposta": resposta_model.resposta,
        "autor": account_management_service.get_user_profile(resposta_model.autor),
    }

    return resposta_dict
