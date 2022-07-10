"""Define signal handlers para o módulo 'accounts'"""
from random import randint

from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from accounts.models import EmailActivationToken


@receiver(signal=post_save, sender=settings.AUTH_USER_MODEL)
def create_user_token(created=False, instance=None, **kwargs):
    """Cria um token de autenticação após o registro do usuário."""
    if created:
        Token.objects.create(user=instance)


@receiver(signal=post_save, sender=settings.AUTH_USER_MODEL)
def create_email_activation_token(created=False, instance=None, **kwargs):
    """Envia token de confirmação do e-mail para o usuário após o registro."""
    if created:
        token = EmailActivationToken.objects.create(
            user=instance, email=instance.email, token=str(randint(0, 999999)).zfill(6)
        )

        EmailMessage(
            to=[instance.email],
            subject="Ativação do cadastro - Ambiente de Monitoria Online",
            body=f"Seu código de ativação: {token.token}",
        ).send()
