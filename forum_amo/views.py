"""
View forum_app
"""
from django import http
from django.core import exceptions
from django.db import IntegrityError, transaction
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_access_policy import AccessViewSetMixin
from rest_framework import response, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


from forum_amo.utils import send_report_mail
import forum_amo.forum_service
from forum_amo.access_policy import DuvidaAccessPolicy, RespostaAccessPolicy
from forum_amo.models import Duvida, Resposta, VotoDuvida

from forum_amo.serializers import (
    DuvidaSerializer,
    RespostaSerializer,
    VotoDuvidaSerializer,
    DenunciaSerializer,
)


class DuvidaFilter(filters.FilterSet):
    """Filtros utilizados nas views de Dúvidas"""

    disciplina = filters.Filter(field_name="disciplina__nome", lookup_expr="icontains")
    disciplina_id = filters.Filter(field_name="disciplina", lookup_expr="exact")


class DuvidaViewSet(AccessViewSetMixin, ModelViewSet):
    """ViewSet referente ao modelo de dúvidas do fórum"""

    access_policy = DuvidaAccessPolicy
    serializer_class = DuvidaSerializer
    queryset = Duvida.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DuvidaFilter
    search_fields = ["titulo"]
    ordering_fields = ["data", "votos"]
    ordering = ["data"]

    @action(methods=["POST", "DELETE"], detail=True)
    def votar(self, request: Request, pk=None):
        """Permite votar em um dúvida"""
        if request.method == "POST":
            dados = {"duvida": pk, "usuario": request.user}
            serializer = VotoDuvidaSerializer()
            try:
                serializer.create(dados)
                return Response(status=status.HTTP_202_ACCEPTED)
            except IntegrityError:
                return Response(status=status.HTTP_409_CONFLICT)
        if request.method == "DELETE":
            dados = {"duvida": pk, "usuario": request.user}
            serializer = VotoDuvidaSerializer()
            try:
                serializer.destroy(dados)
                return Response(status=status.HTTP_204_NO_CONTENT)
            except VotoDuvida.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "example": 5,
                        "description": "id da resposta",
                    }
                },
            }
        },
        responses={
            (status.HTTP_204_NO_CONTENT, "application/json"): {},
            (status.HTTP_404_NOT_FOUND, "application/json"): {
                "type": "object",
                "properties": {
                    "erro": {
                        "type": "object",
                        "properties": {
                            "mensagem": {
                                "type": "string",
                                "example": "Dúvida não encontrada.",
                            }
                        },
                    }
                },
            },
        },
    )
    @action(methods=["POST", "DELETE"], detail=True)
    def correta(self, request: Request, pk=None):  # pylint: disable=unused-argument
        """Permite marcar e desmarcar uma resposta como correta."""
        try:
            duvida = self.get_object()
        except http.Http404:
            return response.Response(
                data={"erro": {"mensagem": "Dúvida não encontrada."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        if request.method == "POST":
            try:
                resposta_pk = request.data.get("id", None)
                resposta = Resposta.objects.get(pk=resposta_pk)
                if resposta.duvida_id == duvida.pk:
                    duvida.resposta_correta.add(resposta.id)
                    duvida.save()
            except exceptions.ObjectDoesNotExist:
                return response.Response(
                    data={"erro": {"mensagem": "Resposta não encontrada."}},
                    status=status.HTTP_404_NOT_FOUND,
                )

        if request.method == "DELETE":
            resposta_pk = request.data.get("id", None)
            duvida.resposta_correta.remove(resposta_pk)
            duvida.save()
            return response.Response(
                data={"sucesso": {"mensagem": "resposta desmarcada como certa."}},
                status=status.HTTP_200_OK,
            )

        return response.Response(
            data={"sucesso": {"mensagem": "a respota foi marcado como certa"}},
            status=status.HTTP_200_OK,
        )

    @action(methods=["POST"], detail=True, url_path="report-duvida")
    def report(self, request):
        """Permite denunciar uma dúvida"""
        duvida = self.get_object()
        data = request.data
        data["duvida"] = duvida.id

        serializer = DenunciaSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            denuncia = serializer.save()
            send_report_mail(denuncia)
            return Response(
                {"success": "Denúncia enviada com sucesso"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RespostaViewSet(AccessViewSetMixin, ModelViewSet):
    """ViewSet referente ao modelo de respostas do fórum"""

    access_policy = RespostaAccessPolicy
    serializer_class = RespostaSerializer
    queryset = Resposta.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["resposta"]
    filterset_fields = ["duvida"]
    ordering_fields = ["data"]
    ordering = ["data"]

    @extend_schema(
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
                    "id": {"type": "integer", "example": 1},
                    "duvida": {"type": "integer", "example": 1},
                    "data": {
                        "type": "string",
                        "example": "2022-09-01T19:31:10.716357-03:00",
                    },
                    "resposta": {
                        "type": "string",
                        "example": "Tem o passo a passo no capítulo 2 do livro.",
                    },
                    "autor": {
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
                    },
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
                                "example": "Resposta não encontrada.",
                            }
                        },
                    }
                },
            },
        },
    )
    def retrieve(self, request, *args, pk=None, **kwargs):
        try:
            resposta = forum_amo.forum_service.get_resposta(pk)
        except exceptions.ObjectDoesNotExist:
            return Response(
                data={"erro": {"mensagem": "Resposta não encontrada."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(resposta, status=200)

    def destroy(self, request, *args, pk=None, **kwargs):
        with transaction.atomic():

            resposta = Resposta.objects.get(id=pk)
            resposta.delete()
            duvida = Duvida.objects.get(id=resposta.duvida.id)
            duvida.quantidade_comentarios -= 1
            duvida.save()

            return response.Response(
                data={"Sucesso": {"mensagem": "Resposta excluída.."}},
                status=status.HTTP_204_NO_CONTENT,
            )

    @action(methods=["POST"], detail=True, url_path="report")
    def report(self, request):
        """Permite denunciar uma resposta"""
        resposta = self.get_object()
        data = request.data

        data["resposta"] = resposta.id
        serializer = DenunciaSerializer(data=data, context={"request": request})

        if serializer.is_valid():
            denuncia = serializer.save()
            send_report_mail(denuncia)
            return Response(
                {"success": "Denúncia enviada com sucesso"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
