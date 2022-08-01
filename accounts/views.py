"""Conjunto de Views do aplicativo 'accounts'."""

import marshmallow
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_access_policy import AccessViewSetMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, mixins, GenericViewSet, ViewSet
from accounts.utils import sanitization_utils
from accounts import account_management_service, errors, access_policy, models
from accounts.serializer import (
    EmailValidationTokenSerializer,
    UserSerializer,
)


class UserRegistration(AccessViewSetMixin, ViewSet):
    """ViewSet para ações relacionadas ao cadastro do usuário."""

    access_policy = access_policy.AccountRegistrationAccessPolicy

    @extend_schema(
        tags=["Autenticação"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "email_str": {"type": "string", "example": "aluno@alu.ufc.br"},
                    "password_str": {
                        "type": "string",
                        "example": "supersecurepassword1",
                    },
                },
            }
        },
        responses={
            (201, "application/json"): OpenApiResponse(
                description="Registro efetuado com sucesso.",
                response={
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "object",
                            "properties": {
                                "auth_token": {
                                    "type": "string",
                                    "example": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
                                },
                            },
                        }
                    },
                },
            )
        },
    )
    def create(self, request):
        """Realiza o cadastro do usuário."""
        unsafe_email = request.data.get("email", "")
        unsafe_password = request.data.get("password", "")

        sanitized_email = sanitization_utils.strip_xss(unsafe_email)

        try:
            _, token_str = account_management_service.create_account(
                sanitized_email, unsafe_password
            )
        except errors.EmailAddressAlreadyExistsError as e:
            response = {
                "error": {"message": e.message, "error_code": e.internal_error_code}
            }
            return Response(data=response, status=e.http_error_code)
        except marshmallow.exceptions.ValidationError as e:
            return Response(data={"error": {"message": e.messages}}, status=422)

        response = {"data": {"auth_token": token_str}}
        return Response(data=response, status=201)


class UserViewSet(AccessViewSetMixin, ModelViewSet):  # pylint: disable=R0901
    """ViewSet para ações relacionadas ao usuário."""

    access_policy = access_policy.UserViewAccessPolicy
    queryset = models.CustomUser.objects.all()
    serializer_class = UserSerializer

    @extend_schema(request=EmailValidationTokenSerializer)
    @action(detail=False, methods=["post"])
    def ativar(self, request):
        """Ativação do email do usuário."""
        try:
            token = models.EmailActivationToken.objects.get(
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

    access_policy = access_policy.UserViewAccessPolicy
    serializer_class = UserSerializer
    queryset = models.CustomUser.objects.all()

    def get_object(self):
        return models.CustomUser.objects.get(pk=self.request.user.pk)
