"""Este módulo contem ações de gerenciamento de contas de Usuário."""

from django.core.mail import send_mail
from django.forms.models import model_to_dict


from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.authtoken.models import Token

from accounts import errors
from accounts.models import CustomUser, EmailActivationToken, Perfil


def create_account(sanitized_email_str: str, unsafe_password_str: str):
    """Realiza a criação de um usuário.

    Args:
        sanitized_email_str: e-mail informado pelo usuário.
        unsafe_password_str: senha informada pelo usuário.
        admin: booleano informando se usuário deve ser administrador.

    Returns:
        Retorna uma instância de Usuário.

    Raises:
        EmailAddressAlreadyExistsError: existe um usuário ativo cadastrado com o e-mail informado.
        ValidationError: ocorreu um erro ao validar dados informados.
    """

    user_model = CustomUser.objects.filter(email=sanitized_email_str).first()

    if user_model:
        if user_model.is_email_active:
            raise errors.EmailAddressAlreadyExistsError("E-mail already in use.")
        send_email_confirmation_token(user_instance=user_model)
        return user_model

    with transaction.atomic():
        user_model = CustomUser.objects.create_user(
            email=sanitized_email_str,
            password=unsafe_password_str,
            is_email_active=False,
        )
        user_model.full_clean()
        user_model.save()

        Perfil.objects.create(usuario=user_model)
        send_email_confirmation_token(user_instance=user_model)

    return user_model


def get_user_profile(user_instance: CustomUser) -> dict:
    """Retorna o perfil de um usuário."""
    profile = model_to_dict(user_instance.perfil)
    profile["foto"] = "https://res.cloudinary.com/dlvmqmqcn/image/upload/v1/" + str(
        user_instance.perfil.foto
    )
    profile["cargos"] = user_instance.cargos
    if profile["curso"]:
        profile["curso"] = user_instance.perfil.curso.nome
    allowed_fields = [
        "id",
        "nome_completo",
        "nome_exibicao",
        "entrada",
        "curso",
        "cargos",
        "foto",
    ]
    for key in list(profile.keys()):
        if key not in allowed_fields:
            profile.pop(key)
    profile["id"] = user_instance.id
    return profile


def update_user_profile(perfil: Perfil, data: dict) -> dict:
    """Atualiza o perfil do usuário."""
    allowed_keys = [
        "nome_completo",
        "nome_exibicao",
        "data_nascimento",
        "matricula",
        "entrada",
        "curso",
        "foto",
    ]

    with transaction.atomic():
        if "curso" in allowed_keys:
            allowed_keys.remove("curso")
            if "curso" in data.keys():
                perfil.curso_id = data["curso"]

        for key, value in data.items():
            if key in allowed_keys:
                setattr(perfil, key, value)

        perfil.full_clean()
        perfil.save()

    return get_user_profile(perfil.usuario)


def send_email_confirmation_token(user_instance):
    """Envia token de confirmação do e-mail para o usuário."""
    # Verificar se já existe um token ativo ou expirado
    existing_token = EmailActivationToken.objects.filter(
        user=user_instance, email=user_instance.email
    ).first()

    if existing_token:
        if existing_token.expires_at > timezone.now():

            token_instance = existing_token
        else:
            existing_token.delete()  # Limpa o token antigo
            token_instance = EmailActivationToken.generate_token(user=user_instance)
    else:
        token_instance = EmailActivationToken.generate_token(user=user_instance)

    subject = "Ativação do cadastro - Ambiente de Monitoria Online"
    body = f"Seu código de ativação: {token_instance.token}"

    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [user_instance.email],
        fail_silently=False,
    )


def confirm_email(user, token):
    """
    Função para autenticação do código enviado para o email do usuário.
    """
    try:
        token_instance = EmailActivationToken.objects.get(
            user=user, token=token, expires_at__gt=timezone.now()
        )
    except EmailActivationToken.DoesNotExist as exc:
        raise errors.EmailConfirmationCodeInactive() from exc

    user.is_email_active = True
    user.save()

    token_instance.delete()

    auth_token = get_user_token(user)
    return auth_token.key


def get_user_token(user):
    """Busca ou cria um Token de autenticação do usuário.

    Args:
        user: uma instância de User.

    Returns:
        Um Token de autenticação do usuário.
    """
    token_model, _ = Token.objects.get_or_create(user=user)
    return token_model
