from rest_framework import serializers


class CursoSerializer(serializers.Serializer):
    nome = serializers.CharField()
    descricao = serializers.CharField()
