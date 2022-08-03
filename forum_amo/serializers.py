"""Serializer do model duvida"""

from rest_framework import serializers

import accounts.models
from forum_amo.models import Duvida

class AutorSerializer(serializers.ModelSerializer):
    """Serializer para exibir autor na dúvida"""


    class Meta:
        model = accounts.models.CustomUser
        fields = ["id", "first_name", "last_name", "email"]



class DuvidaSerializer(serializers.ModelSerializer):
    """Serializer para arquivos"""

    titulo = serializers.CharField(max_length=200)
    descricao = serializers.CharField(max_length=550)
    autor = AutorSerializer(read_only=True)

    def create(self, validated_data):
        nova_duvida = Duvida.objects.create(
            titulo=validated_data["titulo"],
            descricao=validated_data["descricao"],
            autor_id=self.context["request"].user.id
        )

        return nova_duvida


    class Meta:
        model = Duvida
        queryset = Duvida.objects.all()
        fields = ["id", "titulo", "descricao", "autor"]

