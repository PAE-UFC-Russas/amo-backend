"""Testes do modelo de usuário customizado do aplicativo 'accounts'."""

from django.test import TestCase

from accounts.models import CustomUser

PASSWORD = "M@vr8RjZS8LqrjhV"


class CustomUserTest(TestCase):
    """Testes relacionados a CustomUser."""

    fixtures = ["groups.yaml"]

    def test_create_user(self):
        """Verifica a criação de um usuário"""
        CustomUser.objects.create_user(email="usuario@test.com", password=PASSWORD)

        user = CustomUser.objects.first()
        self.assertEqual(user.email, "usuario@test.com")
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Verifica a criação de um administrador."""
        CustomUser.objects.create_superuser(email="usuario@test.com", password=PASSWORD)

        user = CustomUser.objects.first()
        self.assertEqual(user.email, "usuario@test.com")
        self.assertTrue(user.is_superuser)
