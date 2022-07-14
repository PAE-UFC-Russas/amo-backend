"""Testes do aplicativo 'accounts'."""

from django.contrib.auth.hashers import make_password
from django.core import mail
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.serializer import UserRegistrationSerializer, UserSerializer
from .models import CustomUser, EmailActivationToken

PASSWORD = "M@vr8RjZS8LqrjhV"


class UserAuthTest(APITestCase):
    """Verifica a autenticação do usuário."""

    def setUp(self):
        CustomUser.objects.create(
            email="test@user.com", password=make_password(PASSWORD)
        )

    def test_get_user_api_key(self):
        """Verifica que o processo de login retorna uma chave da API válida."""
        token = Token.objects.get(user__email="test@user.com")
        data = {"username": "test@user.com", "password": PASSWORD}
        response = self.client.post(reverse("obtain-api-token"), data, format="json")
        self.assertEqual(response.data["token"], token.key)


class CustomUserTest(TestCase):
    """Testes relacionados a CustomUser."""

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


class UserViewSetTest(APITestCase):
    """Testes relacionados a UserViewSet"""

    def setUp(self) -> None:
        self.client.post(
            reverse("usuario-registrar"),
            {"email": "test@user.com", "password": PASSWORD},
            format="json",
        )
        self.user = CustomUser.objects.first()

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


class UserRegistration(APITestCase):
    """Testes relacionados ao cadastro do usuário."""

    def test_user_registration(self):
        """Verifica a criação de um usuário em UserViewSet"""
        response = self.client.post(
            reverse("usuario-registrar"),
            {"email": "test@user.com", "password": PASSWORD},
            format="json",
        )
        user = CustomUser.objects.first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.auth_token.key, response.data["token"])
        self.assertFalse(user.is_email_active)
        self.assertEqual(response.data, {"token": user.auth_token.key})

    def test_easy_password(self):
        """Verifica que uma senha fácil não é permitida."""
        with self.assertRaises(ValidationError):
            UserRegistrationSerializer().create(
                validated_data={"email": "test@user.com", "password": "password"}
            )

    def test_letters_only_password(self):
        """Verifica que a senha não pode conter apenas letras."""
        with self.assertRaises(ValidationError):
            UserRegistrationSerializer().create(
                validated_data={"email": "test@user.com", "password": "hgfedcba"}
            )

    def test_numbers_only_password(self):
        """Verifica que a senha não pode conter apenas números."""
        with self.assertRaises(ValidationError):
            UserRegistrationSerializer().create(
                validated_data={"email": "test@user.com", "password": "15798452"}
            )

    def test_send_registration_token(self):
        """Verifica o envio do código de ativação do email."""
        self.client.post(
            reverse("usuario-registrar"),
            {"email": "test@user.com", "password": PASSWORD},
            format="json",
        )
        user = CustomUser.objects.first()
        token = EmailActivationToken.objects.first()
        self.assertEqual(user.pk, token.user.pk)
        self.assertIn(f"Seu código de ativação: {token.token}", mail.outbox[0].body)

    def test_email_activation(self):
        """Verifica a confirmação do email, começando com o cadastro do usuário."""
        # realiza o cadastro do usuário
        self.client.post(
            reverse("usuario-registrar"),
            {"email": "test@user.com", "password": PASSWORD},
            format="json",
        )

        # verifica que email não foi confirmardo
        user = CustomUser.objects.first()
        self.assertFalse(user.is_email_active)

        # faz a ativação
        activation_token = EmailActivationToken.objects.first()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {user.auth_token.key}")
        response = self.client.post(
            reverse("usuario-ativar"),
            {"token": f"{activation_token.token}"},
        )

        # verifica se foi ativado com sucesso
        user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(user.is_email_active)

    def test_no_email_token(self):
        """Verifica que erro é retornado em uma tentativa sem o token de confirmação."""
        user = CustomUser.objects.create_user(
            email="usuario@test.com", password=PASSWORD
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {user.auth_token.key}")
        response = self.client.post(
            reverse("usuario-ativar", args=[1]), {"token": "12345hgjkhjk"}
        )
        self.assertEqual(response.status_code, 404)

    def test_no_auth_token(self):
        """Verifica se uma tentativa de validação sem o token de autenticação é recusada."""
        response = self.client.post(reverse("usuario-ativar"), {"token": "123456"})
        self.assertEqual(response.status_code, 401)


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
