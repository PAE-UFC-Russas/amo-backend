"""Serializer do model duvida"""

from rest_framework import serializers

from accounts.models import CustomUser
from forum_amo.models import Duvida, Resposta

class AutorSerializer(serializers.ModelSerializer):
    """Serializer para exibir autor na dúvida e na resposta"""

    class Meta:
        model = CustomUser
        fields = ["id", "first_name", "last_name", "email"]


class DuvidaSerializer(serializers.ModelSerializer):
    """Serializer para dúvidas"""

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
        fields = ["id", "titulo", "descricao", "data", "disciplina"]


class RespostaSerializer(serializers.ModelSerializer):
    """Serializer para respostas"""

    class Meta:
        model = Resposta
        queryset = Resposta.objects.all()
        fields = ["id", "duvida", "resposta", "data", "autor"]

    def create(self, validated_data):
        nova_resposta = Resposta.objects.create(
            autor_id=self.context["request"].user.id,
            duvida_id=validated_data["duvida"].id,
            resposta=validated_data["resposta"],
        )
        return nova_resposta
