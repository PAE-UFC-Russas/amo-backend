"""Ferramentas para auxílio ao testes"""
from accounts import account_management_service
from core import models as core_models
from forum_amo import models as forum_models


def db_create() -> None:
    """Cria um objeto de cada modelo para realizar testes."""

    # Core
    core_models.Curso.objects.create(
        nome="Ciência da Computação",
        descricao="Bacharelado em Ciência da Computação",
    )
    core_models.Disciplinas.objects.create(
        nome="Engenharia de Software",
        descricao="Visão geral dos princípios fundamentais da Engenharia de Software.",
    )

    # Accounts
    account_management_service.create_account(
        sanitized_email_str="test_user@localhost", unsafe_password_str="PASWORD1!"
    )

    # Fórum
    forum_models.Duvida.objects.create(
        disciplina_id=1,
        titulo="Prova1 ",
        descricao="Quais tópicos cairão na prova 1?",
    )
    forum_models.Resposta.objects.create(
        duvida_id=1,
        autor_id=1,
        resposta="Capítulos 1 a 5.",
    )
