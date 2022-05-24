from ast import Is
from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.models import Curso
from core.serializer import CursoSerializer


class CursoViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        cursos = Curso.objects.all()
        serializer = CursoSerializer(cursos, many=True)
        return Response(serializer.data)
