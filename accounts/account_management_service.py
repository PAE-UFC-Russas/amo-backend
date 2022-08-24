"""Este módulo contem ações de gerenciamento de contas de Usuário."""
from datetime import timedelta
from random import randint

from django.core import exceptions, mail
from django.db import transaction
from django.forms.models import model_to_dict
from django.utils import timezone
from rest_framework.authtoken.models import Token

from accounts import schema, errors
from accounts.models import CustomUser, EmailActivationToken, Perfil


def create_account(
    sanitized_email_str: str, unsafe_password_str: str, admin: bool = False
):
    """Realiza a criação de um usuário.

    Args:
        sanitized_email_str: e-mail informado pelo usuário.
        unsafe_password_str: senha informada pelo usuário.
        admin: booleano informando se usuário deve ser administrador

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
        if admin:
            user_model = CustomUser.objects.create_superuser(
                email=sanitized_email_str, password=unsafe_password_str
            )
        else:
            user_model = CustomUser.objects.create_user(
                email=sanitized_email_str, password=unsafe_password_str
            )
        user_model.full_clean()
        user_model.save()

        Perfil.objects.create(usuario=user_model)

    send_email_confirmation_token(user_instance=user_model)

    auth_token_model = get_user_token(user=user_model)

    return user_model, auth_token_model.key


def get_user_profile(user_instance: CustomUser):
    """Retorna o perfil de um usuário."""

    profile = model_to_dict(user_instance.perfil)
    if profile["curso"]:
        profile["curso"] = user_instance.perfil.curso.nome

    allowed_fields = ["nome_exibicao", "entrada", "curso"]

    for key in list(profile.keys()):
        if key not in allowed_fields:
            profile.pop(key)

    return profile


def send_email_confirmation_token(user_instance):
    """Envia token de confirmação do e-mail para o usuário."""

    token = EmailActivationToken.objects.create(
        user=user_instance,
        email=user_instance.email,
        token=str(randint(0, 999999)).zfill(6),
    )

    mail.EmailMessage(
        to=[user_instance.email],
        subject="Ativação do cadastro - Ambiente de Monitoria Online",
        body=f"Seu código de ativação: {token.token}",
    ).send()


def confirm_email(activation_code: str, user: CustomUser):
    """Realiza a confirmação do e-mail de um usuário."""

    try:
        activation_code_model = EmailActivationToken.objects.get(
            token=activation_code, user=user
        )
    except exceptions.ObjectDoesNotExist as error:
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
