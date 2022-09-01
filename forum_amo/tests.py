"""
TESTS forum_app
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.account_management_service import create_account, CustomUser
from core.models import Disciplinas
from forum_amo.models import Duvida, Resposta
from forum_amo.serializers import DuvidaSerializer, RespostaSerializer
from utils import test_utils


class DuvidaTestes(APITestCase):
    """
    Classe de testes para a viewset do modelo de dúvidas
    """

    def setUp(self) -> None:
        _, self.user_token = create_account(
            sanitized_email_str="johndoe@localhost.com",
            unsafe_password_str="password123",
        )
        _, self.admin_token = create_account(
            sanitized_email_str="superjohndoe@localhost.com",
            unsafe_password_str="superpassword123",
            admin=True,
        )
        disciplina = Disciplinas.objects.create(
            nome="teste", descricao="descrição teste"
        )
        self.duvida = Duvida.objects.create(
            titulo="Distribuição Exponencial",
            descricao="Probabilidade e Estatística",
            disciplina=disciplina,
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
            {"id": "2", "titulo": "Recursão", "descricao": "FUP", "disciplina": 1},
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


class RespostaTestes(APITestCase):
    """
    Classe de testes para a viewset do modelo de Respostas.
    """

    def setUp(self) -> None:
        self.user, _ = create_account(
            sanitized_email_str="johndoe@localhost.com",
            unsafe_password_str="password123",
        )
        disciplina = Disciplinas.objects.create(nome="IHC", descricao="teste")
        self.duvida = Duvida.objects.create(
            titulo="Distribuição Exponencial",
            descricao="Probabilidade e Estatística",
            disciplina=disciplina,
        )
        self.resposta = Resposta.objects.create(
            autor=self.user, duvida=self.duvida, resposta="Esforce-se mais"
        )

    def test_listar_respostas(self):
        """Testa o listamento de todas as respostas já criadas"""
        response = self.client.get(
            reverse("respostas-list"),
        )
        self.assertEqual(response.data, [RespostaSerializer(self.resposta).data])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_criar_resposta(self):
        """Teste a criação de uma nova resposta"""
        response = self.client.post(
            reverse("respostas-list"),
            {
                "autor": self.user.id,
                "resposta": "Teorema de Pitágoras",
                "duvida": self.duvida.id,
                "data_criada": "2022-08-25T09:37:46.521258-03:00",
                "id": "1",
            },
            HTTP_AUTHORIZATION=f"Token {self.user.auth_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data,
            (
                RespostaSerializer(
                    Resposta.objects.get(resposta="Teorema de Pitágoras")
                ).data
            ),
        )

    def test_buscar_resposta(self):
        """Testa a busca de uma resposta por meio do id"""
        response = self.client.get(reverse("respostas-detail", args=[1]))
        self.assertEqual(response.data, (RespostaSerializer(self.resposta).data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_deletar_resposta(self):
        """Testa a remoção de uma resposta (resposta existente)"""
        response = self.client.delete(
            reverse("respostas-detail", args=[1]),
            HTTP_AUTHORIZATION=f"Token {self.user.auth_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_deletar_resposta_nao_existente(self):
        """Testa a remoção de uma resposta (resposta não existente)"""
        response = self.client.delete(
            reverse("respostas-detail", args=[16]),
            HTTP_AUTHORIZATION=f"Token {self.user.auth_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_buscar_resposta_pela_duvidas(self):
        """Testa as respostas ao buscá-las pelo id da dúvida"""

        respostas = Resposta.objects.get(duvida=self.duvida)
        self.assertEqual(
            RespostaSerializer(respostas).data, RespostaSerializer(self.resposta).data
        )


class RespostaCorretaTest(APITestCase):
    """Valida que é possível marcar uma resposta como correta."""

    def setUp(self) -> None:
        test_utils.db_create()

    def test_resposta_correta(self):
        """Verifica que o usuário pode selecionar e remover uma resposta como correta."""
        usuario = CustomUser.objects.first()
        duvida = Duvida.objects.first()
        resposta = Resposta.objects.first()
        self.assertIsNone(duvida.resposta_correta_id)

        url = reverse("duvidas-correta", args=[duvida.pk])
        self.client.post(
            url, {"id": resposta.pk}, HTTP_AUTHORIZATION=f"Token {usuario.auth_token}"
        )

        duvida.refresh_from_db()
        self.assertEqual(duvida.resposta_correta_id, resposta.pk)

        self.client.delete(url, HTTP_AUTHORIZATION=f"Token {usuario.auth_token}")
        duvida.refresh_from_db()
        self.assertIsNone(duvida.resposta_correta_id)
