"""Conjunto de Views do aplicativo 'accounts'."""

import marshmallow
from django.core import exceptions
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    extend_schema_view,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_access_policy import AccessViewSetMixin
from rest_framework import status

# from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import mixins, GenericViewSet, ViewSet

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
                    "email": {"type": "string", "example": "aluno@alu.ufc.br"},
                    "password": {
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

    # pylint: disable=C0301
    # @extend_schema(
    #     tags=["Cadastro do Usuário"],
    #     request={
    #         "application/json": {
    #             "type": "object",
    #             "properties": {"token": {"type": "string", "example": "157543"}},
    #         }
    #     },
    #     responses={
    #         (204, "application/json"): {},
    #         (404, "application/json"): {
    #             "type": "object",
    #             "properties": {
    #                 "erro": {
    #                     "type": "object",
    #                     "properties": {
    #                         "mensagem": {
    #                             "type": "string",
    #                             "example": errors.EmailConfirmationCodeNotFound.message,
    #                         },
    #                         "codigo": {
    #                             "type": "integer",
    #                             "example": errors.EmailConfirmationCodeNotFound.internal_error_code,
    #                         },
    #                     },
    #                 }
    #             },
    #         },
    #         (409, "application/json"): {
    #             "type": "object",
    #             "properties": {
    #                 "erro": {
    #                     "type": "object",
    #                     "properties": {
    #                         "mensagem": {
    #                             "type": "string",
    #                             "example": errors.EmailConfirmationCodeExpired.message,
    #                         },
    #                         "codigo": {
    #                             "type": "integer",
    #                             "example": errors.EmailConfirmationCodeExpired.internal_error_code,
    #                         },
    #                     },
    #                 }
    #             },
    #         },
    #     },
    # )
    # @action(methods=["POST"], detail=False)
    # def confirmar_email(self, request):
    #     Realiza a confirmação do email do usuário.
    #     unsafe_activation_code = request.data.get("token", "")

    #     sanitized_activation_code = sanitization_utils.strip_xss(unsafe_activation_code)

    #     try:
    #         account_management_service.confirm_email(
    #             sanitized_activation_code, request.user
    #         )
    #     except errors.EmailConfirmationCodeNotFound as e:
    #         return Response(
    #             data={"erro": {"mensagem": e.message, "codigo": e.internal_error_code}},
    #             status=status.HTTP_404_NOT_FOUND,
    #         )
    #     except errors.EmailConfirmationCodeExpired as e:
    #         return Response(
    #             data={"erro": {"mensagem": e.message, "codigo": e.internal_error_code}},
    #             status=status.HTTP_409_CONFLICT,
    #         )
    #     except errors.EmailConfirmationConflict as e:
    #         return Response(
    #             data={"erro": {"mensagem": e.message, "codigo": e.internal_error_code}},
    #             status=status.HTTP_409_CONFLICT,
    #         )

    #     return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    create=extend_schema(tags=["Usuário"]),
    list=extend_schema(tags=["Usuário"]),
    details=extend_schema(tags=["Usuário"]),
    update=extend_schema(tags=["Usuário"]),
    partial_update=extend_schema(tags=["Usuário"]),
    destroy=extend_schema(tags=["Usuário"]),
)
class UserViewSet(
    AccessViewSetMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):  # pylint: disable=R0901
    """ViewSet para ações relacionadas ao usuário."""

    access_policy = access_policy.UserViewAccessPolicy
    queryset = models.CustomUser.objects.all()
    serializer_class = serializer.UserSerializer

    @extend_schema(
        tags=["Usuário"],
        parameters=[
            OpenApiParameter(
                "id",
                type=OpenApiTypes.STR,
                required=True,
                location="path",
                description="id do usuário ou 'eu', como atalho para o usuário atual.",
            )
        ],
        responses={
            (200, "application/json"): {
                "type": "object",
                "properties": {
                    "perfil": {
                        "type": "object",
                        "properties": {
                            "nome_exibição": {
                                "type": "string",
                                "example": "Francisco Silva",
                            },
                            "curso": {
                                "type": "string",
                                "example": "Ciência da Computação",
                            },
                            "entrada": {"type": "string", "example": "2022.1"},
                        },
                    }
                },
            },
            (404, "application/json"): {
                "type": "object",
                "properties": {
                    "erro": {
                        "type": "object",
                        "properties": {
                            "mensagem": {
                                "type": "string",
                                "example": "Usuário não encontrado.",
                            }
                        },
                    }
                },
            },
        },
    )
    def retrieve(self, request, pk=None):
        """Retorna o perfil de um usuário."""
        try:
            user_model = (
                request.user if pk == "eu" else models.CustomUser.objects.get(pk=pk)
            )   
            perfil = account_management_service.get_user_profile(user_model)
        except exceptions.ObjectDoesNotExist:
            return Response(
                data={"erro": {"mensagem": "Usuário não encontrado."}}, status=404
            )

        return Response(data={"perfil": perfil}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Usuário"],
        parameters=[
            OpenApiParameter(
                "id",
                type=OpenApiTypes.STR,
                required=True,
                location="path",
                description="id do usuário ou 'eu', como atalho para o usuário atual.",
            )
        ],
        request={
                "multipart/form-data": {
                "type": "object",
                "properties": {
                    "nome_completo": {"type": "string", "example": "David Jon Gilmour"},
                    "password": {
                        "type": "string",
                        "example": "supersecurepassword1",
                    },
                    "nome_exibicao": {"type":"string", "example":"David Gilmour"},
                    "data_nascimento": {"type": "string", "example": "1948-06-20"},

                    "matricula": {"type": "string", "example": "123456"},

                    "entrada": {"type": "string", "example": "2021.1"},

                    "curso": {"type": "integer", "example": "1"},
                    "foto": {"type": "file"}
                
                },
            }
        },
        responses={
            (200, "application/json"): {
                "type": "object",
                "properties": {
                    "perfil": {
                        "type": "object",
                        "properties": {

                            "id": {"type": "integer", "example":"1"},
                            "foto": {"type": "file", "example":"192.168.0.1/imagens/foto.jpg"},
                            "nome_exibição": {
                                "type": "string",
                                "example": "Francisco Silva",
                            },
                            "curso": {
                                "type": "string",
                                "example": "Ciência da Computação",
                            },
                            "entrada": {"type": "string", "example": "2022.1"},

                            "cargos": {"type": "list", "example": "[]"},
                        },
                    }
                },
            },
            (400, "application/json"): {
                "type": "object",
                "properties": {
                    "erro": {
                        "type": "object",
                        "properties": {
                            "nome_completo": {
                                "type": "array",
                                "example": ["Este campo não pode estar vazio!"],
                            }
                        },
                    }
                },
            },
        },
    )
    def partial_update(self, request, pk=None):
        """Realiza a atualização dos valores do perfil do usuário."""
        # print(request.data['foto'])
        # models.Perfil.objects.update
        user = request.user if pk == "eu" else self.get_object()
        print(request.data)
        # user.perfil.foto = request.data['foto']
        # user.perfil.save()
        # user.save()
        try:
            perfil = account_management_service.update_user_profile(
                user.perfil, request.data
            )
        # return Response(data={"perfil": perfil}, status=status.HTTP_200_OK)
        except exceptions.ValidationError as e:
            return Response(
                data={"erro": e.error_dict}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            data={"perfil": perfil}, status=status.HTTP_200_OK
        )
