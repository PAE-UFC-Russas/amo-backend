"""
TESTS forum_app
"""
from django.urls import reverse
from rest_framework.test import APITestCase
from forum_amo.models import Duvida
from forum_amo.serializers import DuvidaSerializer
from accounts.models import CustomUser

from rest_framework.test import APIRequestFactory
from django.test import Client


class DuvidaTestes(APITestCase):
    def setUp(self) -> None:
        self.user = CustomUser.objects.create(
            email="johndoe@localhost.com", password="password123"
        )

        self.admin = CustomUser.objects.create_superuser(
            email="superjohndoe@localhost.com", password="superpassword123"
        )

        self.duvida = Duvida.objects.create(
            titulo="Distribuição Exponencial", descricao="Probabilidade e Estatística"
        )

    def test_listar_duvidas(self):
        response = self.client.get(
            reverse("duvidas-list"),
            HTTP_AUTHORIZATION=f"Token {self.user.auth_token.key}",
        )
        self.assertEqual(response.data, [DuvidaSerializer(self.duvida).data])

    def test_criar_duvida(self):
        c = Client()
        dados = [DuvidaSerializer(self.duvida).data.pop("id")]
        response = self.client.post(
            reverse("duvidas-list"),
            {
                "id": "1",
                "titulo": "Distribuição Exponencial",
                "descricao": "Probabilidade e Estatística",
            },
        )
        assert response.status_code == 201

    def test_buscar_duvida(self):

        response = self.client.get(reverse("duvidas-list", args=[1]))
        print(response.status_code)
        """
        response = self.client.get(
            reverse("duvidas-detail", args=[1]),
            HTTP_AUTHORIZATION=f"Token {self.user.auth_token.key}",
        )
        """
        # print(response.data)
        # self.assertEqual(response.data, [DuvidaSerializer(self.duvida).data])
