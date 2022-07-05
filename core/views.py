"""Conjunto de Views do aplicativo 'core'."""

from django_filters.rest_framework import DjangoFilterBackend
from rest_access_policy import AccessViewSetMixin
from rest_framework.viewsets import ModelViewSet

from core.access_policy import CursoAccessPolicy, DisciplinaAccessPolicy
from core.models import Curso, Disciplinas
from core.serializer import CursoSerializer, DisciplinaSerializer


class CursoViewSet(AccessViewSetMixin, ModelViewSet):  # pylint: disable=R0901
    """ViewSet para ações relacionadas a cursos."""

    access_policy = CursoAccessPolicy
    serializer_class = CursoSerializer
    queryset = Curso.objects.all()


class DisciplinaViewSet(AccessViewSetMixin, ModelViewSet):  # pylint: disable=R0901
    """ViewSet para ações relacionadas a disciplinas."""

    access_policy = DisciplinaAccessPolicy
    serializer_class = DisciplinaSerializer
    queryset = Disciplinas.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["cursos"]
