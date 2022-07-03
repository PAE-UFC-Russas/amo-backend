"""Este módulo define os modelos do aplicativo 'accounts'."""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """Define um 'manager' para utilização com CustomUser."""

    def create_user(self, email, password=None, **extra_fields):
        """Cria um usuário."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
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
    email = models.EmailField(_("email address"), blank=False, unique=True)
    is_email_active = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.email


class EmailActivationToken(models.Model):
    """Token enviado ao usuário para ativação de seu email."""

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    email = models.EmailField(blank=False)
    token = models.CharField(unique=True, blank=False, max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True)
