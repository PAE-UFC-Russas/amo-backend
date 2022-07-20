"""Conjunto de Views do aplicativo 'accounts'."""

from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema
from rest_access_policy import AccessViewSetMixin
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, mixins, GenericViewSet

from accounts.access_policy import UserViewAccessPolicy
from accounts.models import EmailActivationToken, CustomUser
from accounts.serializer import (
    EmailValidationTokenSerializer,
    UserSerializer,
    UserRegistrationSerializer,
)


class UserViewSet(AccessViewSetMixin, ModelViewSet):  # pylint: disable=R0901
    """ViewSet para ações relacionadas ao usuário."""

    access_policy = UserViewAccessPolicy
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    @extend_schema(request=UserRegistrationSerializer, responses=AuthTokenSerializer)
    @action(detail=False, methods=["post"])
    def registrar(self, request):
        """Realiza o cadastro de um novo usuário."""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"token": user.auth_token.key})
        return Response(serializer.data)

    @extend_schema(request=EmailValidationTokenSerializer)
    @action(detail=False, methods=["post"])
    def ativar(self, request):
        """Ativação do email do usuário."""
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


class CurrentUserUpdateView(
    AccessViewSetMixin, mixins.UpdateModelMixin, GenericViewSet
):
    """Possibilita a atualização do perfil do usuário atual."""

    access_policy = UserViewAccessPolicy
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()

    def get_object(self):
        return CustomUser.objects.get(pk=self.request.user.pk)
