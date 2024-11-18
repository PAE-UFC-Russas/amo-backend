"""Serializer do model duvida"""

from django.db import transaction
from rest_framework import serializers

from accounts.serializer import UserSerializer
from core.models import Disciplinas
from forum_amo.models import Duvida, Resposta, VotoDuvida, Denuncia


class DuvidaVotouField(serializers.Field):
    """Campo para informar se o usuário atual votou na dúvida."""

    def get_attribute(self, instance):
        try:
            return VotoDuvida.objects.filter(
                usuario=self.context["request"].user, duvida=instance
            ).exists()
        except KeyError:
            return False

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        raise NotImplementedError


class DenunciaSerializer(serializers.ModelSerializer):
    """Serializer para denúncias"""

    class Meta:
        model = Denuncia
        fields = ["id", "reason", "descricao", "duvida", "resposta", "autor"]
        read_only_fields = ["autor"]

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["autor"] = request.user
        return super().create(validated_data)


class DuvidaSerializer(serializers.ModelSerializer):
    """Serializer para arquivos"""

    titulo = serializers.CharField(max_length=200)
    descricao = serializers.CharField(max_length=550)
    disciplina = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=Disciplinas.objects.all()
    )
    resposta_correta = serializers.PrimaryKeyRelatedField(read_only=True)
    autor = UserSerializer(read_only=True)
    votos = serializers.IntegerField(read_only=True)
    votou = DuvidaVotouField(read_only=True)
    quantidade_comentarios = serializers.IntegerField(read_only=True)

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
            "votos",
            "votou",
            "quantidade_comentarios",
        ]


class RespostaSerializer(serializers.ModelSerializer):
    """Serializer para respostas"""

    autor = UserSerializer(read_only=True)

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
        duvida = Duvida.objects.get(id=validated_data["duvida"].id)
        duvida.quantidade_comentarios += 1
        duvida.save()
        return nova_resposta


class VotoDuvidaSerializer(serializers.ModelSerializer):
    """Serializer para voto em dúvidas"""

    usuario = UserSerializer(read_only=True)

    class Meta:
        model = VotoDuvida
        queryset = VotoDuvida.objects.all()
        fields = ["id", "usuario", "duvida"]

    def create(self, validated_data):
        with transaction.atomic():
            voto = VotoDuvida.objects.create(
                usuario_id=validated_data["usuario"].id,
                duvida_id=validated_data["duvida"],
            )
            duvida = Duvida.objects.get(pk=validated_data["duvida"])
            duvida.votos += 1
            duvida.save()

        return voto

    def destroy(self, validated_data):
        "Exclui o voto de um usuário em uma dúvida"
        with transaction.atomic():
            voto = VotoDuvida.objects.get(
                usuario=validated_data["usuario"].id,
                duvida=validated_data["duvida"],
            )
            voto.delete()
            duvida = Duvida.objects.get(pk=validated_data["duvida"])
            duvida.votos -= 1
            duvida.save()
