from django.shortcuts import render
from rest_framework.viewsets import ViewSet

from rest_framework import viewsets
from rest_framework.decorators import action

from rest_framework.response import Response
from core.models import Curso
from core.serializer import CursoSerializer
from rest_framework.decorators import api_view


class CursoViewSet(ViewSet):
    def list(self, request):
        cursos = Curso.objects.all()
        serializer = CursoSerializer(cursos, many=True)
        return Response(cursos)
    def create(self, request):
        serializer=CursoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)






        
