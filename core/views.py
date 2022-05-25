from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import action

from rest_framework.response import Response
from core.models import Curso
from core.serializer import CursoSerializer
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes
from rest_framework.decorators import permission_classes



class CursoViewSet(ViewSet):
    

    #@permission_classes([IsAuthenticated])
    def list(self, request):
        cursos = Curso.objects.all()
        serializer = CursoSerializer(cursos, many=True)
        return Response(serializer.data)
    def create(self, request):
        serializer=CursoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)






        
