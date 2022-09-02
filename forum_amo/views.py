"""
View forum_app
"""
from django import http
from django.core import exceptions
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend

from drf_spectacular.utils import extend_schema
from rest_access_policy import AccessViewSetMixin
from rest_framework import response, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet

from forum_amo.access_policy import DuvidaAccessPolicy, RespostaAccessPolicy
from forum_amo.models import Duvida, Resposta
from forum_amo.serializers import DuvidaSerializer, RespostaSerializer


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
    ordering_fields = ["data"]
    ordering = ["data"]

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
                    duvida.resposta_correta = resposta
                    duvida.save()
            except exceptions.ObjectDoesNotExist:
                return response.Response(
                    data={"erro": {"mensagem": "Resposta não encontrada."}},
                    status=status.HTTP_404_NOT_FOUND,
                )

        if request.method == "DELETE" and duvida.resposta_correta_id is not None:
            duvida.resposta_correta = None
            duvida.save()

        return response.Response(status=status.HTTP_204_NO_CONTENT)


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
