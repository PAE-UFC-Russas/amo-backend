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

    class Meta:
        model = Duvida
        queryset = Duvida.objects.all()
        fields = ["id", "titulo", "descricao"]


class RespostaSerializer(serializers.ModelSerializer):
    """Serializer para respostas"""

    autor = AutorSerializer(read_only=True)
    duvida = DuvidaSerializer(read_only=True)
    resposta = serializers.CharField(max_length=750)
    data_criada = serializers.DateTimeField()

    class Meta:
        model = Resposta
        queryset = Resposta.objects.all()
        fields = ["id", "duvida", "resposta", "data_criada", "autor"]

    def create(self, validated_data):
        print(validated_data)
        nova_resposta = Resposta.objects.create(
            autor=self.context["request"].user.id,
            duvida_id=validated_data["duvida"],
            resposta=validated_data["resposta"],
            data_criada=validated_data["data_criada"],
        )
        return nova_resposta
