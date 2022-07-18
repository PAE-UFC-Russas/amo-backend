"""Testes de controle de acesso do aplicativo 'accounts'."""

from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser, EmailActivationToken

PASSWORD = "M@vr8RjZS8LqrjhV"


class UserAccessPolicyTestCase(APITestCase):
    """Verifica o controle de acesso para UserViewSet"""

    def setUp(self) -> None:
        self.user = CustomUser.objects.create(
            email="user@localhost", password=make_password("password")
        )

    def test_unauthenticated_access(self):
        """Verifica controle de acesso para usuários não autenticados"""
        with self.subTest("Registrar Usuário"):
            response = self.client.post(
                reverse("usuario-registrar"),
                {"email": "user2@localhost", "password": "ajfsd9p&*aa"},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("Ativar email"):
            response = self.client.post(reverse("usuario-ativar"))
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest("Login"):
            # A view de login é fornecida pelo Django Rest Framework, por isso
            # não é controlada por UserViewAccessPolicy
            response = self.client.post(
                reverse("obtain-api-token"),
                {"username": "user@localhost", "password": "password"},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("Listar"):
            response = self.client.get(reverse("usuario-list"))
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest("Detalhes"):
            response = self.client.get(reverse("usuario-list"), args=[1])
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest("Atualizar"):
            response = self.client.patch(
                reverse("usuario-detail", args=[1]),
                {"perfil": {"matricula": "000002"}},
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_access(self):
        """Verifica controle de acesso para usuários autenticados"""
        with self.subTest("Registrar"):
            response = self.client.post(
                reverse("usuario-registrar"),
                {"email": "user1@localhost", "password": "f7aw87ho2q!"},
                HTTP_AUTHORIZATION=f"Token {self.user.auth_token.key}",
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest("Ativar email"):
            email_token = EmailActivationToken.objects.create(
                user=self.user, email=self.user.email, token="000000"
            )
            response = self.client.post(
                reverse("usuario-ativar"),
                {"token": email_token.token},
                HTTP_AUTHORIZATION=f"Token {self.user.auth_token.key}",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("Login"):
            response = self.client.post(
                reverse("obtain-api-token"),
                {"username": "user@localhost", "password": "password"},
                HTTP_AUTHORIZATION=f"Token {self.user.auth_token.key}",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("Listar"):
            response = self.client.get(
                reverse("usuario-list"),
                HTTP_AUTHORIZATION=f"Token {self.user.auth_token.key}",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("Detalhes"):
            response = self.client.get(
                reverse("usuario-list"),
                args=[1],
                HTTP_AUTHORIZATION=f"Token {self.user.auth_token.key}",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("Atualizar usuário"):
            user_ = CustomUser.objects.create(
                email="user_patch@localhost", password=PASSWORD
            )
            response = self.client.patch(
                reverse("usuario-detail", args=[user_.pk]),
                {"perfil": {"matricula": "321123"}},
                format="json",
                HTTP_AUTHORIZATION=f"Token {user_.auth_token.key}",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("Atualizar outro usuário"):
            user_ = CustomUser.objects.create(
                email="user_patch2@localhost", password=PASSWORD
            )
            response = self.client.patch(
                reverse("usuario-detail", args=[2]),
                {"perfil": {"matricula": "000002"}},
                format="json",
                HTTP_AUTHORIZATION=f"Token {user_.auth_token.key}",
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
