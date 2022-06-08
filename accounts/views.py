from random import randint

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from accounts.models import EmailActivationToken
from accounts.serializer import EmailValidationTokenSerializer, UserSerializer


class UserViewSet(ViewSet):
    @extend_schema(request=UserSerializer, responses=UserSerializer)
    @action(detail=False, methods=["post"])
    def registrar(self, request):
        """Realiza o cadastro de um novo usuário."""
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = EmailActivationToken(
                user=user, email=user.email, token=str(randint(0, 999999)).zfill(6)
            )
            token.save()
            email = EmailMessage(
                to=[user.email],
                subject="Ativação do cadastro - Amebiente de Monitoria Online",
                body=f"Seu código de ativação: {token.token}",
            )
            email.send()
        return Response(serializer.data)

    @extend_schema(request=EmailValidationTokenSerializer)
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def ativar(self, request, pk=None):
        try:
            token = EmailActivationToken.objects.get(
                token=request.data["token"], email=request.user.email
            )
        except ObjectDoesNotExist:
            return Response(None, 404)
        token.activated_at = now()
        token.save()
        request.user.is_email_active = True
        request.user.save()
        return Response(None, 200)
