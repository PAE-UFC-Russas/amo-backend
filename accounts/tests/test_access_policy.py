"""Testes de controle de acesso do aplicativo 'accounts'."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser, EmailActivationToken

# from accounts.models import EmailActivationToken
from core.models import Curso

PASSWORD = "M@vr8RjZS8LqrjhV"


class UserAccessPolicyTestCase(APITestCase):
    """Verifica o controle de acesso para UserViewSet"""

    fixtures = ["groups.yaml"]

    def setUp(self) -> None:
        self.email = "user@localhost.com"
        self.password = PASSWORD
        self.client.post(
            reverse("registrar-list"),
            {"email": "user@localhost.com", "password": PASSWORD},
            format="json",
        )

        self.user = CustomUser.objects.first()

        activation_token = EmailActivationToken.objects.first()
        response = self.client.post(
            "/registrar/confirmar-email/",
            {"token": f"{activation_token.token}"},
        )

        form = {"username": "user@localhost.com", "password": PASSWORD}
        response = self.client.post("/usuario/login/", data=form)
        self.user_auth_token = response.json()["token"]

        Curso.objects.create(nome="Computação", descricao="Computação")

    def test_unauthenticated_access(self):
        """Verifica controle de acesso para usuários não autenticados"""
        with self.subTest("Registrar Usuário"):
            response = self.client.post(
                reverse("registrar-list"),
                {"email": "user2@pae.localhost", "password": "ajfsd9p&*aa"},
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        with self.subTest("Ativar email"):
            response = self.client.post("/registrar/confirmar-email/")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        with self.subTest("Login"):
            # A view de login é fornecida pelo Django Rest Framework, por isso
            # não é controlada por UserViewAccessPolicy
            response = self.client.post(
                "/usuario/login/",
                {"username": "user@localhost.com", "password": PASSWORD},
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
                HTTP_AUTHORIZATION=f"Token {self.user_auth_token}",
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        with self.subTest("Ativar email"):
            email_token = EmailActivationToken.objects.create(
                user=self.user, email=self.user.email, token="000000"
            )
            response = self.client.post(
                "/registrar/confirmar-email/",
                {"token": email_token.token},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        with self.subTest("Login"):
            response = self.client.post(
                reverse("obtain-api-token"),
                {"username": "user@localhost.com", "password": PASSWORD},
                HTTP_AUTHORIZATION=f"Token {self.user_auth_token}",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("Listar"):
            response = self.client.get(
                reverse("usuario-list"),
                HTTP_AUTHORIZATION=f"Token {self.user_auth_token}",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("Detalhes"):
            response = self.client.get(
                reverse("usuario-list"),
                args=[1],
                HTTP_AUTHORIZATION=f"Token {self.user_auth_token}",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("Atualizar usuário"):
            response = self.client.patch(
                reverse("usuario-detail", args=["eu"]),
                {
                    "nome_completo": "Novo Usuário",
                    "nome_exibicao": "Novo",
                    "data_nascimento": "2000-12-30",
                    "matricula": "000000",
                    "curso": 1,
                    "ano_entrada": "2022.1",
                },
                format="json",
                HTTP_AUTHORIZATION=f"Token {self.user_auth_token}",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("Atualizar outro usuário"):
            response = self.client.patch(
                reverse("usuario-detail", args=[2]),
                {"perfil": {"matricula": "000002"}},
                format="json",
                HTTP_AUTHORIZATION=f"Token {self.user_auth_token}",
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
