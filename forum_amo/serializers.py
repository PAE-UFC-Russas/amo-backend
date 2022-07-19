from rest_framework import serializers
from forum_amo.models import Duvida


class FileSerializer(serializers.ModelSerializer):
    titulo = serializers.CharField(max_length=200)
    descricao = serializers.CharField(max_length=550)

    class Meta:
        model = Duvida
        fields = ["id", "titulo"]
