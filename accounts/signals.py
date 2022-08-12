"""Define signal handlers para o módulo 'accounts'"""

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from accounts.models import Perfil


@receiver(signal=post_save, sender=settings.AUTH_USER_MODEL)
def create_user_token(created=False, instance=None, **kwargs):
    """Cria um token de autenticação após o registro do usuário."""
    if created:
        Token.objects.create(user=instance)


@receiver(signal=post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(instance=None, created=None, **kwargs):
    """Cria o perfil após a criação do usuário."""
    if created:
        Perfil.objects.create(usuario=instance)
