"""Testes de autenticação do aplicativo 'accounts'."""

from django.urls import reverse
from rest_framework.test import APITestCase

from accounts import account_management_service

PASSWORD = "M@vr8RjZS8LqrjhV"


class UserAuthTest(APITestCase):
    """Verifica a autenticação do usuário."""

    def setUp(self):
        _, self.token = account_management_service.create_account(
            sanitized_email_str="test@user.com",
            unsafe_password_str=PASSWORD,
        )

    def test_get_user_api_key(self):
        """Verifica que o processo de login retorna uma chave da API válida."""

        data = {"username": "test@user.com", "password": PASSWORD}
        response = self.client.post(reverse("obtain-api-token"), data, format="json")
        self.assertEqual(response.data["token"], self.token)
