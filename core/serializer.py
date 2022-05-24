from rest_framework import serializers
from .models import Curso


class CursoSerializer(serializers.HyperlinkedModelSerializer):
    nome = serializers.CharField()
    descricao = serializers.CharField()

    class Meta:
        model = Curso
        fields = ["id", "nome", "descricao"]
