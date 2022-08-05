"""Serializer do model duvida"""

from rest_framework import serializers

from forum_amo.models import Duvida, Resposta


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

    autor = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    duvida_id = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    resposta = serializers.CharField(max_length=750)
    data_criada = serializers.DateTimeField()

    class Meta:
        Model = Resposta
        queryset = Resposta.objects.all()
        fields = ["id", "duvida_id", "resposta", "data_criada", "autor"]
