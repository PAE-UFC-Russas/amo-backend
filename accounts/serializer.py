"""Este módulo contém os serializadores utilizados na aplicação 'accounts'."""
from django.contrib.auth.password_validation import validate_password
from drf_spectacular.utils import extend_schema_field
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from accounts.models import CustomUser, EmailActivationToken, Perfil
from core.models import Curso


class PerfilCursoSerializer(serializers.ModelSerializer):
    """Define um serializador para Curso dentro de um Perfil.
    Esta classe foi criada apenas para a documentação da view 'update' do usuário."""

    id = serializers.IntegerField()
    nome = serializers.CharField(read_only=True)
    descricao = serializers.CharField(read_only=True)

    class Meta:
        model = Curso
        fields = ["id", "nome", "descricao"]


@extend_schema_field(field=PerfilCursoSerializer)
class CursoRelatedField(serializers.RelatedField):
    """Este field permite a leitura apenas do id e retornar o serializer de
    Curso na view de atualização do usuário/perfil."""

    queryset = Curso.objects.all()

    def to_internal_value(self, data):
        curso = self.queryset.get(id=data)
        return PerfilCursoSerializer(curso).instance

    def to_representation(self, value):
        return PerfilCursoSerializer(value).data


class PerfilSerializer(WritableNestedModelSerializer):
    """Serializador do modelo Perfil."""

    curso = CursoRelatedField()

    class Meta:
        model = Perfil
        fields = [
            "nome_completo",
            "nome_exibicao",
            "data_nascimento",
            "matricula",
            "curso",
        ]


class UserSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    """Serializador do modelo CustomUser."""

    email = serializers.EmailField(read_only=True)
    perfil = PerfilSerializer()

    class Meta:
        model = CustomUser
        fields = ["id", "email", "perfil"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializador usado para o cadastro do usuário."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = CustomUser(email=validated_data["email"])
        validate_password(validated_data["password"], user=user)
        user.set_password(validated_data["password"])
        user.save()
        return user

    class Meta:
        model = CustomUser
        fields = ["email", "password"]


class EmailValidationTokenSerializer(serializers.ModelSerializer):
    """Serializador do modelo EmailValidationToken."""

    class Meta:
        model = EmailActivationToken
        fields = ["token"]
