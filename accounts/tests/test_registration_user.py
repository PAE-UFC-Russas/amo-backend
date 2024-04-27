from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CustomUser
from accounts.models import EmailActivationToken
import datetime

class UserRegistrationAndEmailConfirmationTest(TestCase):
    """Testes para registro de usuário e confirmação de email."""

    def setUp(self):
        """Configurações iniciais para cada teste."""
        self.client = APIClient()
        self.user_data = {
            "email": "test@example.com",
            "password": "safePassword123"
        }
        self.email_token = EmailActivationToken.objects.create(
            user=self.user,
            token="valid-token",
            expires_at=datetime.datetime.now() + datetime.timedelta(hours=24)
        )

    def test_user_registration(self):
        """Testa o registro de um novo usuário."""
        response = self.client.post('/api/user/register/', self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Verifique seu e-mail para ativar sua conta", response.data["message"])

    def test_email_confirmation(self):
        """Testa a confirmação de email do usuário."""
        # Confirmando o e-mail
        confirm_data = {"token": self.email_token.token}
        response = self.client.post('/api/user/confirmar-email/', confirm_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("E-mail confirmado com sucesso", response.data["message"])

        # Verificando se o usuário está ativo
        user = CustomUser.objects.get(email=self.user_data["email"])
        self.assertTrue(user.is_email_active)

    def test_email_confirmation_with_invalid_token(self):
        """Testa a falha na confirmação do email com um token inválido."""
        confirm_data = {"token": "invalid-token"}
        response = self.client.post('/api/user/confirmar-email/', confirm_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Token inválido ou expirado", response.data["error"])
