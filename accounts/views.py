"""Conjunto de Views do aplicativo 'accounts'."""

from contextvars import Token

from django.forms import ValidationError

from accounts.schema import validate_password
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
from rest_framework.decorators import action, authentication_classes, permission_classes
# from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from django.utils import timezone
from datetime import datetime


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
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed




class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if not user.is_email_active:
            raise AuthenticationFailed('Credenciais inválidas ou conta inativa.')
        
        token = Token.objects.get(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })
    
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
        unsafe_email = request.data.get("email", "")
        unsafe_password = request.data.get("password", "")
        sanitized_email = sanitization_utils.strip_xss(unsafe_email)
       

        try:
            models.user_model = account_management_service.create_account(
                sanitized_email, unsafe_password
            )
            return Response(
                {"message": "Usuário criado com sucesso. Verifique seu e-mail para ativar sua conta."},
                status=201
            )
        except errors.EmailAddressAlreadyExistsError as e:
            return Response(
                {"error": {"message": e.message, "error_code": e.internal_error_code}},
                status=e.http_error_code
            )
        except marshmallow.exceptions.ValidationError as e:
            return Response({"error": {"message": e.messages}}, status=422)
        

    @action(methods=['post'], detail=False, url_path='confirmar-email')
    @extend_schema(
        tags=["Cadastro do Usuário"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "token": {
                        "type": "string",
                        "description": "Token de ativação enviado por e-mail",
                        "example": "af23f2"
                    }
                }
            }
        },
        responses={
            (200, "application/json"): OpenApiResponse(
                description="E-mail confirmado com sucesso.",
                response={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "example": "E-mail confirmado com sucesso."},
                        "auth_token": {"type": "string", "example": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"}
                    }
                }
            ),
            (400, "application/json"): OpenApiResponse(
                description="Erro na confirmação do e-mail",
                response={
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "Token inválido ou expirado."
                        }
                    }
                }
            )
        }
    )
    def confirm_email(self, request):
        token = request.data.get('token')
        if not token:
            return Response({"error": "Token não informado."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token_instance = models.EmailActivationToken.objects.get(token=token, expires_at__gt=timezone.now())
            user = token_instance.user
            user.is_email_active = True
            user.save()
            token_instance.delete()

            auth_token = account_management_service.get_user_token(user)
            return Response({
                "message": "E-mail confirmado com sucesso.",
                "auth_token": auth_token.key 
            }, status=status.HTTP_200_OK)
        except models.EmailActivationToken.DoesNotExist:
            return Response({"error": "Token inválido ou expirado."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




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
        user = request.user if pk == "eu" else self.get_object()
        try:
            perfil = account_management_service.update_user_profile(
                user.perfil, request.data
            )
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
    

    @extend_schema(
        tags=["Usuário"],
        parameters=[
            OpenApiParameter(
                "Email",
                type=OpenApiTypes.STR,
                required=True,
                location="path",
                description="Email do usuário",
            )
        ],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "example": "usuario@gmail.com"
                    },
                
                },
            },
        },
        responses={
            (200, "application/json"): {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Email de redefinição de senha enviado com sucesso."
                    },
                },
            },
            (404, "application/json"): {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Usuário não encontrado."
                    },
                },
            },
            (500, "application/json"): {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Erro interno do servidor."
                    },
                },
            },
        },

    )  

    @action(methods=['POST'], detail=False, url_path='solicitar-redefinicao-senha')
    def solicitar_redefinicao_senha(self, request):
        email = request.data.get('email')
        request.session['email'] = email
        if not email:
            return Response({"error": "Email não informado."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = models.CustomUser.objects.get(email=email)
            token = account_management_service.password_reset_email(user)
            return Response({"message": "Email de redefinição de senha enviado com sucesso."}, status=status.HTTP_200_OK)
        except models.CustomUser.DoesNotExist:
            return Response({"error": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    @extend_schema(
        tags=["Usuário"],
        parameters=[
            OpenApiParameter(
                "Token",
                type=OpenApiTypes.STR,
                required=True,
                location="path",
                description="Token de redefinição de senha",
            )
        ],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "token": {
                        "type": "string",
                        "example": "af23f2"
                    }
                }
            }
        },
        responses={
            (200, "application/json"): {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Token válido."
                    },
                },
            },
            (400, "application/json"): {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Token inválido ou expirado."
                    },
                },
            },
            (500, "application/json"): {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Erro interno do servidor."
                    },
                },
            },
        },
    )
    @action(methods=['POST'], detail=False, url_path='verificar-token')
    def verificar_token(self, request):
        token = request.data.get('token')
        if not token:
            return Response({"error": "Token não informado."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token_instance = models.EmailActivationToken.objects.get(token=token, expires_at__gt=timezone.now())
            request.session['token_verification'] = True
            return Response({"message": "Token válido."}, status=status.HTTP_200_OK)
        except models.EmailActivationToken.DoesNotExist:
            return Response({"error": "Token inválido ou expirado."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    @extend_schema(
        tags=["Usuário"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "senha": {
                        "type": "string",
                        "example": "supersecurepassword1"
                    }
                }
            }
        },
        responses={
            (200, "application/json"): {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Senha redefinida com sucesso."
                    },
                },
            },
            (400, "application/json"): {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Senha inválida."
                    },
                },
            },
        },
    )
    @action(methods=['POST'], detail=False, url_path='redefinir-senha')
    def redefinir_senha(self, request):
        if not request.session.get('token_verification', False):
            return Response({"error": "Verificação de token não realizada."}, status=status.HTTP_400_BAD_REQUEST)

        email = request.session.get('email')
        if not email:
            return Response({"error": "Email não encontrado."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_password(request.data)
            user = models.CustomUser.objects.get(email=email)
            user.set_password(request.data['senha'])
            user.save()
            
            return Response({"message": "Senha redefinida com sucesso."}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        