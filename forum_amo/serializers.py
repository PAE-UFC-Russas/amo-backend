from rest_framework import serializers
from forum_amo.models import Duvida
class FileSerializer(serializers.Serializer):
    titulo = serializers.CharField(max_length=200)
    descricao = serializers.CharField(max_length=550)
    privacidade_autor = serializers.BooleanField(default=False)
    arquivo = serializers.FileField(max_length=None)
    def create(self, validated_data):
        return Duvida.objects.create(**validated_data)
    class Meta:
        model = Duvida
        fields = ["id", "titulo", "descricao", "privacidade_autor", "arquivo"]
