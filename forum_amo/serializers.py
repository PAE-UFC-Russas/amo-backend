"""Serializer do model duvida"""

from rest_framework import serializers

from accounts.models import CustomUser
from core.models import Disciplinas
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
    disciplina = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=Disciplinas.objects.all()
    )
    resposta_correta = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Duvida
        queryset = Duvida.objects.all()
        fields = ["id", "titulo", "descricao", "data", "disciplina", "resposta_correta"]


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
