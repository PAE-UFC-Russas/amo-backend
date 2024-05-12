"""Testes do cadastro do usuário do aplicativo 'accounts'."""

# from django.core import mail

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

# from accounts import account_management_service
from accounts.models import CustomUser  # , EmailActivationToken

PASSWORD = "M@vr8RjZS8LqrjhV"


class UserRegistration(APITestCase):
    """Testes relacionados ao cadastro do usuário."""

    fixtures = ["groups.yaml"]

    def test_user_registration(self):
        """Verifica a criação de um usuário em UserViewSet"""
        response = self.client.post(
            reverse("registrar-list"),
            {"email": "alanisoliveira39@gmail.com", "password": PASSWORD},
            format="json",
        )
        user = CustomUser.objects.first()
        self.assertEqual(response.status_code, 201)
        self.assertFalse(user.is_email_active)
        self.assertEqual(response.data, {"data": {"auth_token": user.auth_token.key}})

    def test_letters_only_password(self):
        """Verifica que a senha não pode conter apenas letras."""
        response = self.client.post(
            reverse("registrar-list"),
            {"email": "alanisbig10@gmail.com", "password": "hgfedcba"},
        )

        self.assertContains(
            response,
            "Senha deve conter pelo menos um número.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    def test_numbers_only_password(self):
        """Verifica que a senha não pode conter apenas números."""
        response = self.client.post(
            reverse("registrar-list"),
            {"email": "test@user.com", "password": "15798452"},
        )

        self.assertContains(
            response,
            "Senha deve conter pelo menos uma letra.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    # def test_send_registration_token(self):
    #     """Verifica o envio do código de ativação do email."""
    #     self.client.post(
    #         reverse("registrar-list"),
    #         {"email": "test@user.com", "password": PASSWORD},
    #         format="json",
    #     )
    #     user = CustomUser.objects.first()
    #     token = EmailActivationToken.objects.first()
    #     self.assertEqual(user.pk, token.user.pk)
    #     self.assertIn(f"Seu código de ativação: {token.token}", mail.outbox[0].body)

    #   def test_email_activation(self):
    #     """Verifica a confirmação do email, começando com o cadastro do usuário."""
    #     # realiza o cadastro do usuário
    #     self.client.post(
    #         reverse("registrar-list"),
    #         {"email": "test@user.com", "password": PASSWORD},
    #         format="json",
    #     )

    #     # verifica que email não foi confirmado
    #     user = CustomUser.objects.first()
    #     self.assertFalse(user.is_email_active)

    #     # faz a ativação
    #     activation_token = EmailActivationToken.objects.first()
    #     self.client.credentials(HTTP_AUTHORIZATION=f"Token {user.auth_token.key}")
    #     response = self.client.post(
    #         reverse("registrar-confirmar-email"),
    #         {"token": f"{activation_token.token}"},
    #     )

    #     # verifica se foi ativado com sucesso
    #     user.refresh_from_db()
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     self.assertTrue(user.is_email_active)

    # def test_no_email_token(self):
    #     """Verifica que erro é retornado em uma tentativa sem o token de confirmação."""
    #     _, token = account_management_service.create_account(
    #         sanitized_email_str="usuario@test.com", unsafe_password_str=PASSWORD
    #     )
    #     self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    #     response = self.client.post(
    #         reverse("registrar-confirmar-email", args=[1]), {"token": "12345hgjkhjk"}
    #     )
    #     self.assertEqual(response.status_code, 404)

    # def test_no_auth_token(self):
    #     """Verifica se uma tentativa de validação sem o token de autenticação é recusada."""
    #     response = self.client.post(
    #         reverse("registrar-confirmar-email"), {"token": "123456"}
    #     )
    #     self.assertEqual(response.status_code, 401)
