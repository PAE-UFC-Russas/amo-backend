"""Este módulo define os modelos do aplicativo 'accounts'."""



from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import Curso
from monitorias.settings import MEDIA_ROOT

from datetime import timedelta, datetime
from django.utils import timezone
import secrets

class CustomUserManager(BaseUserManager):
    """Define um 'manager' para utilização com CustomUser."""

    def create_user(self, email, password=None, **extra_fields):
        """Cria um usuário."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        # Essa linha, quando não há nenhum usuário registrado,
        # retorna um erro «Group matching does not exit"
        # Ao invés disso, utilizei a função Group.objects.get_or_create()
        # user.groups.add(Group.objects.get_or_create(name="aluno"))
        group, _ = Group.objects.get_or_create(name="aluno")
        user.groups.add(group)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Cria um administrador."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """Define um usuário customizado para utilizar o email para autenticação."""

    username = None
    first_name = None
    last_name = None
    email = models.EmailField(_("email address"), blank=False, unique=True)
    is_email_active = models.BooleanField(default=False)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    @property
    def cargos(self):
        """Retorna a lista de cargos do usuário."""
        return [group.name for group in self.groups.all()]

    def __str__(self):
        return self.email


class Perfil(models.Model):
    """Representa o perfil do usuário na aplicação.

    Attributes:
        usuario: Refere ao usuário dono do perfil.
        nome_completo: Nome completo do usuário.
        nome_exeibição: Nome que será exibido para os outros usuários.
        data_nascimento: Data de nascimento do usuário.
        matricula: Número de matrícula do usuário. Para alunos e no SIGAA, professores no SIGEP.
        curso: Curso em que o aluno está matriculado. Este campo é ignorado para professores.
        entrada: Ano e semestre de entrada do aluno no curso. Exemplo: 2022.1
    """

    usuario = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="perfil"
    )
    foto = models.ImageField(blank=True, null=True, upload_to=MEDIA_ROOT)
    nome_completo = models.CharField(max_length=255)
    nome_exibicao = models.CharField(max_length=32)
    data_nascimento = models.DateField(null=True)
    matricula = models.CharField(max_length=6, null=True)
    curso = models.ForeignKey(Curso, on_delete=models.SET_NULL, blank=True, null=True)
    entrada = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        validators=[
            validators.RegexValidator(
                regex=r"\d{4}\.[12]", message="Campo não está formatado corretamente."
            ),
        ],
    )

    def __str__(self):
        return self.usuario.email


class EmailActivationToken(models.Model):
    """Token enviado ao usuário para ativação de seu email."""

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    email = models.EmailField(blank=False)
    token = models.CharField(unique=True, blank=False, max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=timezone.make_aware(datetime.now() + timedelta(minutes=15)))

    @staticmethod
    def generate_token(user):
        """Gera um token de ativação de email."""
        token = secrets.token_hex(3)
        expiration_date = timezone.now() + timedelta(minutes=15)
        token_instance = EmailActivationToken.objects.create(
            user=user,
            email=user.email,
            token=token,
            expires_at=expiration_date
        )
        return token_instance