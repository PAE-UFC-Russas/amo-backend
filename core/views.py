from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.models import Curso, Disciplinas
from accounts.models import CustomUser
from rest_framework.decorators import action
from core.serializer import (
    CursoSerializer,
    DisciplinaRequestSerializer,
    DisciplinaResponseSerializer,
)
from drf_spectacular.utils import extend_schema

from django.core.exceptions import ObjectDoesNotExist


class CursoViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CursoSerializer

    def list(self, request):

        """Retorna uma lista de Cursos"""
        cursos = Curso.objects.all()
        serializer = CursoSerializer(cursos, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Adiciona um Curso"""
        serializer = CursoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        try:
            curso = Curso.objects.get(id=pk)
            curso.delete()
            return Response("Curso deletado")
        except ObjectDoesNotExist:
            return Response("Não deletado/Não existe este curso")

    def partial_update(self, request, *args, **kwargs):
        curso = Curso.objects.get(pk=kwargs.get("pk"))
        serializer = CursoSerializer(curso, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class DisciplinaViewSet(ViewSet):
    # permission_classes = [IsAuthenticated]

    @extend_schema(responses=DisciplinaResponseSerializer)
    def list(self, request):
        """Retorna uma lista de disciplinas"""

        disciplinas = Disciplinas.objects.all()
        serializer = DisciplinaResponseSerializer(disciplinas, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=DisciplinaRequestSerializer, responses=DisciplinaResponseSerializer
    )
    def create(self, request):
        """Adiciona uma disciplina"""
        serializer = DisciplinaRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
