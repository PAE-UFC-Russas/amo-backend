from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.models import Curso
from core.serializer import CursoSerializer


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
