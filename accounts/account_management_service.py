"""Este módulo contem ações de gerenciamento de contas de Usuário."""
from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone
from rest_framework.authtoken.models import Token

from accounts import schema, errors
from accounts.models import CustomUser, EmailActivationToken


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
            email=sanitized_email_str, password=unsafe_password_str
        )
        user_model.full_clean()
        user_model.save()

    auth_token_model = get_user_token(user=user_model)

    return user_model, auth_token_model.key


def confirm_email(activation_code: str, user: CustomUser):
    """Realiza a confirmação do e-mail de um usuário."""

    try:
        activation_code_model = EmailActivationToken.objects.get(
            token=activation_code, user=user
        )
    except ObjectDoesNotExist as error:
        raise errors.EmailConfirmationCodeNotFound() from error

    if activation_code_model.created_at + timedelta(hours=24) <= timezone.now():
        raise errors.EmailConfirmationCodeExpired()

    if (
        user.is_email_active
        or activation_code_model.email != user.email
        or activation_code_model.activated_at is not None
    ):
        raise errors.EmailConfirmationConflict()

    with transaction.atomic():
        activation_code_model.activated_at = timezone.now()
        activation_code_model.save()

        user.is_email_active = True
        user.save()


def get_user_token(user):
    """Busca ou cria um Token de autenticação do usuário.

    Args:
        user: uma instância de User.

    Returns:
        Um Token de autenticação do usuário.
    """
    token_model, _ = Token.objects.get_or_create(user=user)
    return token_model
