from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from core.models import Curso
from core.serializer import CursoSerializer


class CursoViewSet(ViewSet):
    def list(self, request):
        cursos = Curso.objects.all()
        serializer = CursoSerializer(cursos, many=True)
        return Response(serializer.data)
