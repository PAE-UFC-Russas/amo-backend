"""Este módulo contem ações de gerenciamento de contas de Usuário."""
from django.contrib.auth.hashers import make_password
from django.db import transaction
from rest_framework.authtoken.models import Token

from accounts import schema, errors
from accounts.models import CustomUser


def create_account(sanitized_email_str: str, unsafe_password_str: str):
    """Realiza a criação de um usuário.

    Args:
        sanitized_email_str: e-mail informado pelo usuário.
        unsafe_password_str: senha informada pelo usuário.

    Returns:
        Retorna uma tupla contendo uma instância de Usuário e seu Token de autenticação.

    Raises:
        EmailAddressAlreadyExistsError: existe um usuário cadastrado com o e-mail informado.
        ValidationError: ocorreu um erro ao validar dados informados.
    """
    schema.UserRegistration().load(
        {"email": sanitized_email_str, "password": unsafe_password_str}
    )

    if CustomUser.objects.filter(email=sanitized_email_str).exists():
        raise errors.EmailAddressAlreadyExistsError()

    with transaction.atomic():
        user_model = CustomUser.objects.create_user(
            email=sanitized_email_str, password=make_password(unsafe_password_str)
        )
        user_model.full_clean()
        user_model.save()

    auth_token_model = get_user_token(user=user_model)

    return user_model, auth_token_model.key


def get_user_token(user):
    """Busca ou cria um Token de autenticação do usuário.

    Args:
        user: uma instância de User.

    Returns:
        Um Token de autenticação do usuário.
    """
    token_model, _ = Token.objects.get_or_create(user=user)
    return token_model
