"""Este módulo contém os serializadores utilizados na aplicação 'core'."""
from rest_framework import serializers

from core.models import Curso, Disciplinas


class CursoSerializer(serializers.HyperlinkedModelSerializer):
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

    class Meta:
        model = Disciplinas
        queryset = Disciplinas.objects.all()
        fields = ["id", "nome", "descricao", "cursos"]
