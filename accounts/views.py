"""Conjunto de Views do aplicativo 'accounts'."""

import marshmallow
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_access_policy import AccessViewSetMixin
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, mixins, GenericViewSet, ViewSet

from accounts import (
    account_management_service,
    errors,
    access_policy,
    models,
    serializer,
)
from accounts.utils import sanitization_utils


class UserRegistration(AccessViewSetMixin, ViewSet):
    """ViewSet para ações relacionadas ao cadastro do usuário."""

    access_policy = access_policy.AccountRegistrationAccessPolicy

    @extend_schema(
        tags=["Cadastro do Usuário"],
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

    @extend_schema(
        tags=["Cadastro do Usuário"],
        request={
            "application/json": {
                "type": "object",
                "properties": {"token": {"type": "string", "example": "157543"}},
            }
        },
        responses={
            (204, "application/json"): {},
            (404, "application/json"): {
                "type": "object",
                "properties": {
                    "erro": {
                        "type": "object",
                        "properties": {
                            "mensagem": {
                                "type": "string",
                                "example": errors.EmailConfirmationCodeNotFound.message,
                            },
                            "codigo": {
                                "type": "integer",
                                "example": errors.EmailConfirmationCodeNotFound.internal_error_code,
                            },
                        },
                    }
                },
            },
            (409, "application/json"): {
                "type": "object",
                "properties": {
                    "erro": {
                        "type": "object",
                        "properties": {
                            "mensagem": {
                                "type": "string",
                                "example": errors.EmailConfirmationCodeExpired.message,
                            },
                            "codigo": {
                                "type": "integer",
                                "example": errors.EmailConfirmationCodeExpired.internal_error_code,
                            },
                        },
                    }
                },
            },
        },
    )
    @action(methods=["POST"], detail=False)
    def confirmar_email(self, request):
        """Realiza a confirmação do email do usuário."""
        unsafe_activation_code = request.data.get("token", "")

        sanitized_activation_code = sanitization_utils.strip_xss(unsafe_activation_code)

        try:
            account_management_service.confirm_email(
                sanitized_activation_code, request.user
            )
        except errors.EmailConfirmationCodeNotFound as e:
            return Response(
                data={"erro": {"mensagem": e.message, "codigo": e.internal_error_code}},
                status=status.HTTP_404_NOT_FOUND,
            )
        except errors.EmailConfirmationCodeExpired as e:
            return Response(
                data={"erro": {"mensagem": e.message, "codigo": e.internal_error_code}},
                status=status.HTTP_409_CONFLICT,
            )
        except errors.EmailConfirmationConflict as e:
            return Response(
                data={"erro": {"mensagem": e.message, "codigo": e.internal_error_code}},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(AccessViewSetMixin, ModelViewSet):  # pylint: disable=R0901
    """ViewSet para ações relacionadas ao usuário."""

    access_policy = access_policy.UserViewAccessPolicy
    queryset = models.CustomUser.objects.all()
    serializer_class = serializer.UserSerializer


class CurrentUserUpdateView(
    AccessViewSetMixin, mixins.UpdateModelMixin, GenericViewSet
):
    """Possibilita a atualização do perfil do usuário atual."""

    access_policy = access_policy.UserViewAccessPolicy
    serializer_class = serializer.UserSerializer
    queryset = models.CustomUser.objects.all()

    def get_object(self):
        return models.CustomUser.objects.get(pk=self.request.user.pk)
