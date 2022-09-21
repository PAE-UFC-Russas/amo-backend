"""Este módulo contém os serializadores utilizados na aplicação 'core'."""
from rest_framework import serializers

from accounts.models import Perfil
from core.models import Curso, Disciplinas


class MonitorSerializer(serializers.ModelSerializer):
    """Define um serializer para exibição de monitores de disciplinas."""

    nome_exibicao = serializers.CharField(source="perfil.nome_exibicao")

    class Meta:
        model = Perfil
        fields = ["id", "nome_exibicao"]


class CursoSerializer(serializers.ModelSerializer):
    """Serializador do modelo Curso."""

    nome = serializers.CharField()
    descricao = serializers.CharField()

    def create(self, validated_data):
        return Curso.objects.create(**validated_data)

    class Meta:
        model = Curso
        fields = ["id", "nome", "descricao"]


class DisciplinaSerializer(serializers.ModelSerializer):
    """Serializer utilizado para responder ao cliente."""

    id = serializers.IntegerField(read_only=True)
    nome = serializers.CharField()
    descricao = serializers.CharField()
    cursos = CursoSerializer(many=True, read_only=True)
    monitores = MonitorSerializer(read_only=True, many=True)
    professores = MonitorSerializer(read_only=True, many=True)

    class Meta:
        model = Disciplinas
        queryset = Disciplinas.objects.all()
        fields = ["id", "nome", "descricao", "cursos", "monitores", "professores"]
