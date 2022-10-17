"""Conjunto de Views do aplicativo 'core'."""
from django_filters.rest_framework import DjangoFilterBackend
from rest_access_policy import AccessViewSetMixin
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ModelViewSet

from core import access_policy, filters
from core.models import Agendamento, Curso, Disciplinas
from core.serializer import (
    AgendamentoRequestSerializer,
    AgendamentoSerializer,
    CursoSerializer,
    DisciplinaSerializer,
)


class CursoViewSet(AccessViewSetMixin, ModelViewSet):  # pylint: disable=R0901
    """ViewSet para ações relacionadas a cursos."""

    access_policy = access_policy.CursoAccessPolicy
    serializer_class = CursoSerializer
    queryset = Curso.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["nome"]


class DisciplinaViewSet(AccessViewSetMixin, ModelViewSet):  # pylint: disable=R0901
    """ViewSet para ações relacionadas a disciplinas."""

    access_policy = access_policy.DisciplinaAccessPolicy
    serializer_class = DisciplinaSerializer
    queryset = Disciplinas.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["cursos"]
    search_fields = ["nome"]


class AgendamentoViewSet(AccessViewSetMixin, ModelViewSet):
    """Ações do agendamento de atendimento."""

    access_policy = access_policy.AgendamentoAccessPolicy
    serializer_class = AgendamentoSerializer
    filterset_class = filters.AgendamentoFilter
    queryset = Agendamento.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["assunto", "descricao"]
    ordering = ["data"]
    ordering_fields = ["data"]

    def perform_create(self, serializer):
        """Salva o agendamento adicionando o usuário atual como solicitante."""
        serializer.save(solicitante=self.request.user)

    def get_request_serializer(self):
        """Altera o serializer nas requisições."""
        return AgendamentoRequestSerializer
