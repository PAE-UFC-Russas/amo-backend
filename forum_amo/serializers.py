"""Serializer do model duvida"""

from rest_framework import serializers
from forum_amo.models import Duvida


class DuvidaSerializer(serializers.ModelSerializer):
    """Serializer para arquivos"""

    titulo = serializers.CharField(max_length=200)
    descricao = serializers.CharField(max_length=550)

    class Meta:
        model = Duvida
        fields = ["id", "titulo", "descricao"]
