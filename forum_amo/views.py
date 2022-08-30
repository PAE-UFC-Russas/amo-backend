"""
View forum_app
"""
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from forum_amo.models import Duvida, Resposta
from forum_amo.serializers import DuvidaSerializer, RespostaSerializer


class DuvidaFilter(filters.FilterSet):
    """Filtros utilizados nas views de Dúvidas"""

    disciplina = filters.Filter(field_name="disciplina__nome", lookup_expr="icontains")
    disciplina_id = filters.Filter(field_name="disciplina", lookup_expr="exact")


class DuvidaViewSet(ModelViewSet):
    """ViewSet referente ao modelo de dúvidas do fórum"""

    permission_classes = [IsAuthenticatedOrReadOnly]

    serializer_class = DuvidaSerializer
    queryset = Duvida.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DuvidaFilter
    search_fields = ["titulo"]
    ordering_fields = ["data"]
    ordering = ["data"]


class RespostaViewSet(ModelViewSet):
    """ViewSet referente ao modelo de respostas do fórum"""

    permission_classes = [IsAuthenticatedOrReadOnly]

    serializer_class = RespostaSerializer
    queryset = Resposta.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["resposta"]
    filterset_fields = ["duvida"]
    ordering_fields = ["data"]
    ordering = ["data"]

    def destroy(self, request, pk=None):  # pylint: disable=W0221
        resposta = Resposta.objects.get(id=pk)
        if request.user.id == resposta.autor.id:
            resposta.delete()
            return Response("", status.HTTP_200_OK)
        return Response("", status.HTTP_401_UNAUTHORIZED)
