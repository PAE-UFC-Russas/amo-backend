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
from rest_framework.decorators import action

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
    # create=extend_schema(tags=["Usuário"]),
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
    queryset = models.CustomUser.objects.all().order_by("id")
    serializer_class = serializer.UserSerializer
    # @extend_schema(
    #     tags=["Usuário"],
    #     request={
    #             "multipart/form-data": {
    #             "type": "object",
    #             "properties": {
    #                 "nome_completo": {"type": "string", "example": "David Jon Gilmour"},
    #                 "password": {
    #                     "type": "string",
    #                     "example": "supersecurepassword1",
    #                 },
    #                 "nome_exibicao": {"type":"string", "example":"David Gilmour"},
    #                 "data_nascimento": {"type": "string", "example": "1948-06-20"},

    #                 "matricula": {"type": "string", "example": "123456"},

    #                 "entrada": {"type": "string", "example": "2021.1"},

    #                 "curso": {"type": "integer", "example": "1"},
    #                 "foto": {"type": "file"}
    #             },
    #         }
    #     },
    #     responses={
    #         (200, "application/json"): {
    #             "type": "object",
    #             "properties": {
    #                 "sucesso": {
    #                     "type": "object",
    #                     "properties": {
    #                         "id": {"type": "string", "example":"Perfil criado com sucesso!"},
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
    #                             "example": "Já existe um perfil para esse usuário. Considere utilizar o método PATCH",
    #                         }
    #                     },
    #                 }
    #             },
    #         },
    #     },
    # })
    # def create(self, request):
    #     user = models.CustomUser.objects.get(email=request.user)
    #     resul = account_management_service.update_user_profile(user.perfil, request.data)
    #     print(resul)
    #     # if user.perfil.nome_completo == "":
    #     #     with transaction.atomic():
    #     #         user.perfil.nome_completo = request.data['nome_completo']
    #     #         user.perfil.nome_exibicao = request.data['nome_exibicao']
    #     #         user.perfil.data_nascimento = request.data['data_nascimento']
    #     #         user.perfil.matricula = request.data['matricula']
    #     #         user.perfil.entrada = request.data['entrada']
    #     #         user.perfil.curso = models.Curso.objects.get(pk=request.data['curso'])
    #     #         user.perfil.foto = request.data['foto']
    #     #         user.perfil.save()
    #     #         user.save()
    #     #         perfil = account_management_service.get_user_profile(user)
    #     # else:
    #     #     return Response(data={"erro": {"mensagem": "Já existe um perfil para esse usuário. Considere utilizar o método PATCH"}}, status=status.HTTP_409_CONFLICT)

    #     # return Response(data=perfil, status=status.HTTP_200_OK)

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
                    "nome_exibicao": {"type": "string", "example": "David Gilmour"},
                    "data_nascimento": {"type": "string", "example": "1948-06-20"},
                    "matricula": {"type": "string", "example": "123456"},
                    "entrada": {"type": "string", "example": "2021.1"},
                    "curso": {"type": "integer", "example": "1"},
                    "foto": {"type": "file"},
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
                            "id": {"type": "integer", "example": "1"},
                            "foto": {
                                "type": "file",
                                "example": "192.168.0.1/imagens/foto.jpg",
                            },
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

        return Response(data={"perfil": perfil}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["usuario"],
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
            "application/json": {
                "type": "object",
                "properties": {
                    "senha_velha": {
                        "type": "string",
                        "example": "securepassword_velha",
                    },
                    "senha_nova": {
                        "type": "string",
                        "example": "supersecurepassword_nova",
                    },
                    "confirma": {
                        "type": "string",
                        "example": "supersecurepassword_nova",
                    },
                },
            }
        },
        responses={
            (200, "application/json"): {
                "type": "object",
                "properties": {
                    "sucesso": {
                        "type": "string",
                        "example": "senha alterada com sucesso!",
                    },
                },
            },
            (403, "application/json"): {
                "type": "object",
                "properties": {
                    "erro": {"type": "string", "example": "senhas não coincidem"},
                },
            },
            (400, "application/json"): {
                "type": "object",
                "properties": {
                    "erro": {"type": "string", "example": "senha atual incorreta"},
                },
            },
        },
    )
    @action(methods=["POST"], detail=True)
    def mudar(self, request, pk=None):
        """
        Função para alterar senha do usuário.
        Recebe como parâmetros: senha_velha; senha_nova; confirma (confirmação de senha_nova)
        """

        user_model = (
            request.user if pk == "eu" else models.CustomUser.objects.get(pk=pk)
        )
        if user_model.check_password(request.data["senha_velha"]) is True:
            if request.data["senha_nova"] == request.data["confirma"]:
                user_model.set_password(request.data["senha_nova"])
                user_model.save()

                return Response(
                    data={"sucesso": "senha alterada com sucesso!"},
                    status=status.HTTP_200_OK,
                )

            return Response(
                data={"erro": "senhas não coincidem"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            data={"erro": "senha atual incorreta"}, status=status.HTTP_403_FORBIDDEN
        )
