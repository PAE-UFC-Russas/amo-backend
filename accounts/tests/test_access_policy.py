"""Testes de controle de acesso do aplicativo 'accounts'."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts import account_management_service
from accounts.models import EmailActivationToken

PASSWORD = "M@vr8RjZS8LqrjhV"


class UserAccessPolicyTestCase(APITestCase):
    """Verifica o controle de acesso para UserViewSet"""

    def setUp(self) -> None:
        self.user, self.token = account_management_service.create_account(
            sanitized_email_str="user@localhost", unsafe_password_str=PASSWORD
        )

    def test_unauthenticated_access(self):
        """Verifica controle de acesso para usuários não autenticados"""
        with self.subTest("Registrar Usuário"):
            response = self.client.post(
                reverse("registrar-list"),
                {"email": "user2@pae.localhost", "password": "ajfsd9p&*aa"},
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        with self.subTest("Ativar email"):
            response = self.client.post(reverse("registrar-confirmar-email"))
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest("Login"):
            # A view de login é fornecida pelo Django Rest Framework, por isso
            # não é controlada por UserViewAccessPolicy
            response = self.client.post(
                reverse("obtain-api-token"),
                {"username": "user@localhost", "password": PASSWORD},
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
                reverse("registrar-list"),
                {"email": "user1@localhost", "password": "f7aw87ho2q!"},
                HTTP_AUTHORIZATION=f"Token {self.token}",
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest("Ativar email"):
            email_token = EmailActivationToken.objects.create(
                user=self.user, email=self.user.email, token="000000"
            )
            response = self.client.post(
                reverse("registrar-confirmar-email"),
                {"token": email_token.token},
                HTTP_AUTHORIZATION=f"Token {self.token}",
            )
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.subTest("Login"):
            response = self.client.post(
                reverse("obtain-api-token"),
                {"username": "user@localhost", "password": PASSWORD},
                HTTP_AUTHORIZATION=f"Token {self.token}",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("Listar"):
            response = self.client.get(
                reverse("usuario-list"),
                HTTP_AUTHORIZATION=f"Token {self.token}",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("Detalhes"):
            response = self.client.get(
                reverse("usuario-list"),
                args=[1],
                HTTP_AUTHORIZATION=f"Token {self.token}",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("Atualizar usuário"):
            user, token = account_management_service.create_account(
                sanitized_email_str="user_patch@localhost",
                unsafe_password_str=PASSWORD,
            )
            response = self.client.patch(
                reverse("usuario-detail", args=[user.pk]),
                {"perfil": {"matricula": "321123"}},
                format="json",
                HTTP_AUTHORIZATION=f"Token {token}",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("Atualizar outro usuário"):
            user, token = account_management_service.create_account(
                sanitized_email_str="user_patch2@localhost",
                unsafe_password_str=PASSWORD,
            )
            response = self.client.patch(
                reverse("usuario-detail", args=[2]),
                {"perfil": {"matricula": "000002"}},
                format="json",
                HTTP_AUTHORIZATION=f"Token {token}",
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
