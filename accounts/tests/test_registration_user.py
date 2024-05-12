# pylint: skip-file
# accounts/tests/test_registration_user.py
from django.urls import reverse
from rest_framework import status
from accounts.models import CustomUser
from accounts.models import EmailActivationToken
import datetime


class UserRegistrationTest(APITestCase):
    """Testa a criação de conta e a geração do token de confirmação de e-mail."""

    def test_user_registration_and_email_confirmation_token(self):
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

    def test_email_confirmation(self):
        """Testa a confirmação de email do usuário."""
        # Confirmando o e-mail
        confirm_data = {"token": self.email_token.token}
        response = self.client.post("/api/user/confirmar-email/", confirm_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("E-mail confirmado com sucesso", response.data["message"])

        email_token = EmailActivationToken.objects.filter(user=user).first()
        self.assertIsNotNone(
            email_token, "Token de confirmação de e-mail não foi gerado."
        )

        print(f"Token de confirmação gerado: {email_token.token}")

        self.assertIn("auth_token", response.data["data"])
