"""Testes de autenticação do aplicativo 'accounts'."""

from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.models import CustomUser

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
