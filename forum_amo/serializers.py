"""Serializer do model duvida"""

from rest_framework import serializers
from core.models import Disciplinas
from forum_amo.models import Duvida, Resposta
from accounts.models import CustomUser
from accounts.serializer import PerfilSerializer


class AutorSerializer(serializers.ModelSerializer):
    """Serializer para exibir autor na dúvida"""

    id = serializers.IntegerField()
    perfil = PerfilSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ["id", "perfil"]


class DuvidaSerializer(serializers.ModelSerializer):
    """Serializer para arquivos"""

    titulo = serializers.CharField(max_length=200)
    descricao = serializers.CharField(max_length=550)
    disciplina = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=Disciplinas.objects.all()
    )
    resposta_correta = serializers.PrimaryKeyRelatedField(read_only=True)
    autor = AutorSerializer(read_only=True)

    def create(self, validated_data):
        nova_duvida = Duvida.objects.create(
            titulo=validated_data["titulo"],
            descricao=validated_data["descricao"],
            disciplina_id=validated_data["disciplina"].pk,
            autor_id=self.context["request"].user.id,
        )

        return nova_duvida

    class Meta:
        model = Duvida
        queryset = Duvida.objects.all()
        fields = [
            "id",
            "titulo",
            "descricao",
            "autor",
            "data",
            "disciplina",
            "resposta_correta",
        ]


class RespostaSerializer(serializers.ModelSerializer):
    """Serializer para respostas"""

    autor = AutorSerializer(read_only=True)

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
