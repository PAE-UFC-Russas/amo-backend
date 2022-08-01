"""Testes sobre UserViewSet do aplicativo 'accounts'."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser
from accounts.serializer import UserSerializer
from core.models import Curso

PASSWORD = "M@vr8RjZS8LqrjhV"


class UserViewSetTest(APITestCase):
    """Testes relacionados a UserViewSet"""

    def setUp(self) -> None:
        self.client.post(
            reverse("registrar-list"),
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

        with self.subTest("Atualizar matrícula"):
            response = self.client.patch(
                reverse("usuario-detail", args=[1]),
                {"perfil": {"matricula": "000000"}},
                format="json",
                HTTP_AUTHORIZATION=f"Token {self.user.auth_token.key}",
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(self.user.perfil.matricula, "000000")

        with self.subTest("Atualizar do Curso"):
            response = self.client.patch(
                reverse("usuario-detail", args=[1]),
                {"perfil": {"curso": 1}},
                format="json",
                HTTP_AUTHORIZATION=f"Token {self.user.auth_token.key}",
            )

            self.user.refresh_from_db()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(self.user.perfil.curso, Curso.objects.first())

        with self.subTest("Atualizar data de entrada"):
            entrada = "2020.1"
            response = self.client.patch(
                reverse("usuario-detail", args=[1]),
                {"perfil": {"entrada": entrada}},
                format="json",
                HTTP_AUTHORIZATION=f"Token {self.user.auth_token.key}",
            )

            self.user.refresh_from_db()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(self.user.perfil.entrada, entrada)

        with self.subTest("Atualizar nome/self"):
            response = self.client.patch(
                reverse("usuario-detail", args=["eu"]),
                {"perfil": {"nome_completo": "Nome do Usuário"}},
                format="json",
                HTTP_AUTHORIZATION=f"Token {self.user.auth_token.key}",
            )

            self.user.refresh_from_db()
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(self.user.perfil.nome_completo, "Nome do Usuário")
