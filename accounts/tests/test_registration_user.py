"""Testes Registro e Ativação de Email"""
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import CustomUser
from accounts.models import EmailActivationToken


class UserRegistrationTest(APITestCase):
    """Testa a criação de conta e a geração do token de confirmação de e-mail."""

    def setUp(self):
        email = "newuser@example.com"
        password = "SecurePassword123!"

        response = self.client.post(
            reverse("registrar-list"),
            data={"email": email, "password": password},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(
            "Verifique seu e-mail para ativar sua conta", response.data["message"]
        )

    def test_email_activation(self):
        """Verifica a confirmação do email"""
        # verifica que email não foi confirmado
        user = CustomUser.objects.first()
        self.assertFalse(user.is_email_active)

        # faz a ativação
        activation_token = EmailActivationToken.objects.first()
        # self.client.credentials(HTTP_AUTHORIZATION=f"Token {user.auth_token.key}")
        response = self.client.post(
            "/registrar/confirmar-email/",
            {"token": f"{activation_token.token}"},
        )

        # verifica se foi ativado com sucesso
        user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(user.is_email_active)

    def test_email_confirmation(self):
        """Testa a confirmação de email do usuário."""
        # Confirmando o e-mail
        confirm_data = EmailActivationToken.objects.get(email="newuser@example.com")
        data = {"token": confirm_data.token}
        response = self.client.post("/registrar/confirmar-email/", data, format="json")
        # response = self.client.post("/api/user/confirmar-email/", confirm_data.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("E-mail confirmado com sucesso", response.data["message"])

        self.assertIsNotNone(
            confirm_data, "Token de confirmação de e-mail não foi gerado."
        )
        self.assertIn("auth_token", str(response.content))
