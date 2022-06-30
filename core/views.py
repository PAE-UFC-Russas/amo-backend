from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_access_policy import AccessViewSetMixin
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.access_policy import CursoAccessPolicy, DisciplinaAccessPolicy
from core.models import Curso, Disciplinas
from core.serializer import (
    CursoSerializer,
    DisciplinaRequestSerializer,
    DisciplinaResponseSerializer,
)


class CursoViewSet(AccessViewSetMixin, ViewSet):
    access_policy = CursoAccessPolicy
    serializer_class = CursoSerializer

    def list(self, request):
        """Retorna uma lista de Cursos"""
        cursos = Curso.objects.all()
        serializer = CursoSerializer(cursos, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Retorna um Curso"""
        queryset = Curso.objects.all()
        curso = get_object_or_404(queryset, pk=pk)
        serializer = CursoSerializer(curso)
        return Response(serializer.data)

    def create(self, request):
        """Adiciona um Curso"""
        serializer = CursoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)

    @extend_schema(responses={204: None, 404: None})
    def destroy(self, request, pk=None):
        """Remove um Curso"""
        try:
            curso = Curso.objects.get(id=pk)
            curso.delete()
            return Response("", status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response("", status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, *args, **kwargs):
        curso = Curso.objects.get(pk=kwargs.get("pk"))
        serializer = CursoSerializer(curso, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class DisciplinaViewSet(AccessViewSetMixin, ViewSet):
    access_policy = DisciplinaAccessPolicy

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
        return Response(DisciplinaResponseSerializer(serializer.instance).data)
    @extend_schema(
        request=DisciplinaRequestSerializer, responses=DisciplinaResponseSerializer
    )    
    def retrieve(self, request, pk=None):
        """Retorna um Curso"""
        queryset = Disciplinas.objects.all()
        disciplina = get_object_or_404(queryset, pk=pk)
        serializer = DisciplinaRequestSerializer(disciplina)
        return Response(DisciplinaResponseSerializer(serializer.instance).data)

    @extend_schema(responses={204: None, 404: None})
    def destroy(self, request, pk=None):
        """Remove um Curso"""
        try:
            disciplina = Disciplinas.objects.get(id=pk)
            disciplina.delete()
            return Response("", status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response("", status.HTTP_404_NOT_FOUND)
    @extend_schema(
        request=DisciplinaRequestSerializer, responses=DisciplinaResponseSerializer
    )    
    def partial_update(self, request, *args, **kwargs):
        disciplina = Disciplinas.objects.get(pk=kwargs.get("pk"))
        serializer = DisciplinaRequestSerializer(disciplina, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(DisciplinaResponseSerializer(serializer.instance).data)


