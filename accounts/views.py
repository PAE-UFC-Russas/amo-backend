from random import randint
from django.core.mail import EmailMessage
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from accounts.models import CustomUser, EmailActivationToken
from accounts.serializer import UserSerializer


class UserViewSet(ViewSet):
    @extend_schema(request=UserSerializer, responses=UserSerializer)
    def create(self, request):
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
