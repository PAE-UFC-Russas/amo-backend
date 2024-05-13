"""Testes de autenticação do aplicativo 'accounts'."""

from django.urls import reverse
from rest_framework.test import APITestCase
from accounts.models import CustomUser, EmailActivationToken

PASSWORD = "M@vr8RjZS8LqrjhV"


class UserAuthTest(APITestCase):
    """Verifica o login e autenticação do usuário."""

    fixtures = ["groups.yaml"]

    def setUp(self):
        self.client.post(
            reverse("registrar-list"),
            {"email": "test@user.com", "password": PASSWORD},
            format="json",
        )

        self.user = CustomUser.objects.first()

        activation_token = EmailActivationToken.objects.first()
        response = self.client.post(
            "/registrar/confirmar-email/",
            {"token": f"{activation_token.token}"},
        )

        form = {"username": "test@user.com", "password": PASSWORD}
        response = self.client.post("/usuario/login/", data=form)
        self.user_auth_token = response.json()["token"]

    def test_get_user_api_key(self):
        """Verifica que o processo de login retorna uma chave da API válida."""

        data = {"username": "test@user.com", "password": PASSWORD}
        response = self.client.post(reverse("obtain-api-token"), data, format="json")
        self.assertEqual(response.data["token"], self.user_auth_token)
