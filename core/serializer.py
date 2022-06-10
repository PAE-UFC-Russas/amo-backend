from rest_framework import serializers

from core.models import Curso, Disciplinas


class CursoSerializer(serializers.HyperlinkedModelSerializer):
    nome = serializers.CharField()
    descricao = serializers.CharField()

    def create(self, validated_data):
        return Curso.objects.create(**validated_data)

    class Meta:
        model = Curso
        fields = ["id", "nome", "descricao"]


class DisciplinaRequestSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer utilizado para criar e atualizar disciplinas."""

    nome = serializers.CharField()
    descricao = serializers.CharField()
    cursos = serializers.PrimaryKeyRelatedField(many=True, queryset=Curso.objects.all())

    def create(self, validated_data):
        cursos = validated_data.pop("cursos")
        disciplina = Disciplinas.objects.create(**validated_data)
        for curso in cursos:
            disciplina.cursos.add(curso)
        disciplina.save()
        return disciplina

    class Meta:
        model = Disciplinas
        queryset = Disciplinas.objects.all()
        fields = ["id", "nome", "descricao", "cursos"]


class DisciplinaResponseSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer utilizado para responder ao cliente."""

    nome = serializers.CharField()
    descricao = serializers.CharField()
    cursos = CursoSerializer(many=True, read_only=True)

    class Meta:
        model = Disciplinas
        queryset = Disciplinas.objects.all()
        fields = ["id", "nome", "descricao", "cursos"]
