"""
View forum_app
"""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from forum_amo.models import Duvida
from forum_amo.serializers import DuvidaSerializer


class DuvidaViewSet(ModelViewSet):
    """ViewSet referente ao modelo de dúvidas do fórum"""

    permission_classes = [IsAuthenticatedOrReadOnly]

    serializer_class = DuvidaSerializer
    queryset = Duvida.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["titulo"]
