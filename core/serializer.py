from rest_framework import serializers

from core.models import Curso


class CursoSerializer(serializers.HyperlinkedModelSerializer):
    nome = serializers.CharField()
    descricao = serializers.CharField()

    def create(self, validated_data):
        return Curso.objects.create(**validated_data)

    class Meta:
        model = Curso
        fields = ["id", "nome", "descricao"]
