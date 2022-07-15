"""Testes sobre UserViewSet do aplicativo 'accounts'."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.serializer import UserSerializer
from accounts.models import CustomUser
from core.models import Curso

PASSWORD = "M@vr8RjZS8LqrjhV"


class UserViewSetTest(APITestCase):
    """Testes relacionados a UserViewSet"""

    def setUp(self) -> None:
        self.client.post(
            reverse("usuario-registrar"),
            {"email": "test@user.com", "password": PASSWORD},
            format="json",
        )
        self.user = CustomUser.objects.first()

        Curso.objects.create(
            nome="Ciência da Computação",
            descricao="Curso de Bacharelado em Ciência da Computação da UFC em Russas",
        )

    def test_list(self):
        """Verifica a visualização de uma lista e usuários."""
        response = self.client.get(
            reverse("usuario-list"),
            HTTP_AUTHORIZATION=f"Token {self.user.auth_token.key}",
        )

        self.assertEqual(response.data, [UserSerializer(self.user).data])

    def test_retrieve(self):
        """Verifica a visualização de um usuário"""
        response = self.client.get(
            reverse("usuario-detail", args=[1]),
            HTTP_AUTHORIZATION=f"Token {self.user.auth_token.key}",
        )

        self.assertEqual(response.data, UserSerializer(self.user).data)

    def test_patch(self):
        """Verifica a atualização parcial do usuario (no perfil)"""
        response = self.client.patch(
            reverse("usuario-detail", args=[1]),
            {"perfil": {"matricula": "000000"}},
            format="json",
            HTTP_AUTHORIZATION=f"Token {self.user.auth_token.key}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.perfil.matricula, "000000")
