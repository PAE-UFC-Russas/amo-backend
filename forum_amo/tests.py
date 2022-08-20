"""
TESTS forum_app
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.account_management_service import create_account
from forum_amo.models import Duvida
from forum_amo.serializers import DuvidaSerializer


class DuvidaTestes(APITestCase):
    """
    Classe de testes para a viewset do modelo de dúvidas
    """

    def setUp(self) -> None:
        _, self.user_token = create_account(
            sanitized_email_str="user@localhost", unsafe_password_str="password1!"
        )
        _, self.admin_token = create_account(
            sanitized_email_str="superuser@localhost",
            unsafe_password_str="adminpassword1!",
            admin=True,
        )
        self.duvida = Duvida.objects.create(
            titulo="Distribuição Exponencial", descricao="Probabilidade e Estatística"
        )

    def test_listar_duvidas(self):
        """Testa o listamento de todas as dúvidas já criadas"""
        response = self.client.get(
            reverse("duvidas-list"),
        )
        self.assertEqual(response.data, [DuvidaSerializer(self.duvida).data])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_criar_duvida(self):
        """Teste a criação de uma nova dúvida"""
        response = self.client.post(
            reverse("duvidas-list"),
            {
                "id": "2",
                "titulo": "Recursão",
                "descricao": "FUP",
            },
            HTTP_AUTHORIZATION=f"Token {self.user_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data,
            (DuvidaSerializer(Duvida.objects.get(titulo="Recursão")).data),
        )

    def test_buscar_duvida(self):
        """Testa a busca de uma dúvida por meio do id"""
        response = self.client.get(reverse("duvidas-detail", args=[1]))
        self.assertEqual(response.data, (DuvidaSerializer(self.duvida).data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_deletar_duvida(self):
        """Testa a remoção de uma dúvida (dúvida existente)"""
        response = self.client.delete(
            reverse("duvidas-detail", args=[1]),
            HTTP_AUTHORIZATION=f"Token {self.user_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_deletar_duvida_nao_existente(self):
        """Testa a remoção de uma dúvida (dúvida não existente)"""
        response = self.client.delete(
            reverse("duvidas-detail", args=[16]),
            HTTP_AUTHORIZATION=f"Token {self.user_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
