from django.contrib.auth.hashers import make_password
from django.core import mail
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.serializer import UserSerializer

from .models import CustomUser, EmailActivationToken

PASSWORD = "M@vr8RjZS8LqrjhV"


class UserAuthTest(APITestCase):
    def setUp(self):
        user = CustomUser.objects.create(
            email="test@user.com", password=make_password(PASSWORD)
        )
        token = Token.objects.create(user=user)

    def test_get_user_api_key(self):
        token = Token.objects.get(user__email="test@user.com")
        data = {"username": "test@user.com", "password": PASSWORD}
        response = self.client.post(reverse("obtain-api-token"), data, format="json")
        self.assertEqual(response.data["token"], token.key)


class CustomUserTest(TestCase):
    def test_create_user(self):
        CustomUser.objects.create_user(email="usuario@test.com", password=PASSWORD)

        user = CustomUser.objects.first()
        self.assertEqual(user.email, "usuario@test.com")
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        CustomUser.objects.create_superuser(email="usuario@test.com", password=PASSWORD)

        user = CustomUser.objects.first()
        self.assertEqual(user.email, "usuario@test.com")
        self.assertTrue(user.is_superuser)


class UserRegistration(APITestCase):
    def test_user_registration(self):
        response = self.client.post(
            reverse("usuario-registrar"),
            {"email": "test@user.com", "password": PASSWORD},
            format="json",
        )
        user = CustomUser.objects.first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.email, response.data["email"])
        self.assertFalse(user.is_email_active)

    def test_easy_password(self):
        with self.assertRaises(ValidationError):
            UserSerializer().create(
                validated_data={"email": "test@user.com", "password": "password"}
            )

    def test_letters_only_password(self):
        with self.assertRaises(ValidationError):
            UserSerializer().create(
                validated_data={"email": "test@user.com", "password": "hgfedcba"}
            )

    def test_numbers_only_password(self):
        with self.assertRaises(ValidationError):
            UserSerializer().create(
                validated_data={"email": "test@user.com", "password": "15798452"}
            )

    def test_send_registration_token(self):
        response = self.client.post(
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
        auth_token = Token.objects.create(user=user)
        activation_token = EmailActivationToken.objects.first()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {auth_token.key}")
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
        auth_token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {auth_token.key}")
        response = self.client.post(
            reverse("usuario-ativar", args=[1]), {"token": "12345hgjkhjk"}
        )
        self.assertEqual(response.status_code, 404)

    def test_no_auth_token(self):
        """Verifica se uma tentativa de validação sem o token de autenticação é recusada."""
        response = self.client.post(reverse("usuario-ativar"), {"token": "123456"})
        self.assertEqual(response.status_code, 401)


class AccessPolicyTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = CustomUser.objects.create(
            email="user@localhost", password=make_password("password")
        )
        self.token = Token.objects.create(user=self.user)

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

    def test_user_access(self):
        """Verifica controle de acesso para usuários autenticados"""
        with self.subTest("Registrar"):
            response = self.client.post(
                reverse("usuario-registrar"),
                {"email": "user1@localhost", "password": "f7aw87ho2q!"},
                HTTP_AUTHORIZATION=f"Token {self.token.key}",
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest("Ativar email"):
            email_token = EmailActivationToken.objects.create(
                user=self.user, email=self.user.email, token="000000"
            )
            response = self.client.post(
                reverse("usuario-ativar"),
                {"token": email_token.token},
                HTTP_AUTHORIZATION=f"Token {self.token.key}",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("Login"):
            response = self.client.post(
                reverse("obtain-api-token"),
                {"username": "user@localhost", "password": "password"},
                HTTP_AUTHORIZATION=f"Token {self.token.key}",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
