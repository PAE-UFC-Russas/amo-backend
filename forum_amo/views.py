"""
View forum_app
"""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet

from forum_amo.models import Duvida
from forum_amo.serializers import FileSerializer


class DuvidaViewSet(ModelViewSet):
    """ViewSet referente ao modelo de dúvidas do fórum"""

    serializer_class = FileSerializer
    queryset = Duvida.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["titulo"]
