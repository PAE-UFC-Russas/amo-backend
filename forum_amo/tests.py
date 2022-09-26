"""
TESTS forum_app
"""
import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.account_management_service import CustomUser, create_account
from core.models import Disciplinas
from forum_amo.models import Duvida, Resposta
from forum_amo.serializers import DuvidaSerializer, RespostaSerializer
from utils import test_utils


class DuvidaTestes(APITestCase):
    """
    Classe de testes para a viewset do modelo de dúvidas
    """

    fixtures = ["groups.yaml"]

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
            autor_id=1,
        )

    def test_listar_duvidas(self):
        """Testa o listamento de todas as dúvidas já criadas"""
        response = self.client.get(
            reverse("duvidas-list"), HTTP_AUTHORIZATION=f"Token {self.user_token}"
        )
        self.assertEqual(
            json.loads(response.content)["results"],
            [DuvidaSerializer(self.duvida).data],
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_criar_duvida(self):
        """Teste a criação de uma nova dúvida"""
        response = self.client.post(
            reverse("duvidas-list"),
            {
                "titulo": "Recursão",
                "descricao": "FUP",
                "disciplina": 1,
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
        response = self.client.get(
            reverse("duvidas-detail", args=[1]),
            HTTP_AUTHORIZATION=f"Token {self.user_token}",
        )
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

    fixtures = ["groups.yaml"]

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
            autor=self.user,
        )
        self.resposta = Resposta.objects.create(
            autor=self.user, duvida=self.duvida, resposta="Esforce-se mais"
        )

    def test_listar_respostas(self):
        """Testa o listamento de todas as respostas já criadas"""
        response = self.client.get(
            reverse("respostas-list"),
            HTTP_AUTHORIZATION=f"Token {self.user.auth_token}",
        )
        self.assertEqual(
            json.loads(response.content)["results"],
            [RespostaSerializer(self.resposta).data],
        )
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
        response = self.client.get(
            reverse("respostas-detail", args=[1]),
            HTTP_AUTHORIZATION=f"Token {self.user.auth_token}",
        )

        self.assertEqual(
            response.data,
            {
                "id": self.resposta.id,
                "duvida": self.resposta.duvida_id,
                "data": self.resposta.data.astimezone(),
                "resposta": self.resposta.resposta,
                "autor": {
                    "id": self.resposta.autor_id,
                    "nome_exibicao": self.resposta.autor.perfil.nome_exibicao,
                    "curso": self.resposta.autor.perfil.curso_id,
                    "entrada": self.resposta.autor.perfil.entrada,
                    "cargos": ["aluno"],
                },
            },
        )
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

    fixtures = ["groups.yaml"]

    def setUp(self) -> None:
        test_utils.db_create()

    def test_resposta_correta(self):
        """Verifica que o usuário pode selecionar e remover uma resposta como correta."""
        usuario = CustomUser.objects.first()
        duvida = Duvida.objects.first()
        resposta = Resposta.objects.first()
        url = reverse("duvidas-correta", args=[duvida.pk])

        # Verifica o estado inicial, que a dúvida não tem uma resposta correta
        self.assertIsNone(duvida.resposta_correta_id)

        # Seleciona uma resposta como correta
        http_response = self.client.post(
            url, {"id": resposta.pk}, HTTP_AUTHORIZATION=f"Token {usuario.auth_token}"
        )
        self.assertEqual(http_response.status_code, status.HTTP_204_NO_CONTENT)
        duvida.refresh_from_db()
        self.assertEqual(duvida.resposta_correta_id, resposta.pk)

        # "Desmarca" uma resposta como correta
        http_response = self.client.delete(
            url, HTTP_AUTHORIZATION=f"Token {usuario.auth_token}"
        )
        self.assertEqual(http_response.status_code, status.HTTP_204_NO_CONTENT)
        duvida.refresh_from_db()
        self.assertIsNone(duvida.resposta_correta_id)


class VotarNaDuvidaTest(APITestCase):
    """Assegura que é possivel votar e remover o voto de uma dúvida"""

    def setUp(self) -> None:
        test_utils.db_create()

    def test_votar_remove_duvida(self):
        """Testa o voto e a remoção da dúvida"""
        usuario = CustomUser.objects.first()
        duvida = Duvida.objects.first()
        url = reverse("duvidas-votar", args=[duvida.pk])

        self.assertEqual(duvida.votos, 0)

        response = self.client.post(
            url, HTTP_AUTHORIZATION=f"Token {usuario.auth_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        duvida.refresh_from_db()
        self.assertEqual(duvida.votos, 1)

        response = self.client.delete(
            url, HTTP_AUTHORIZATION=f"Token {usuario.auth_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        duvida.refresh_from_db()
        self.assertEqual(duvida.votos, 0)

    def test_voto_ja_existe(self):
        """Testa o usuário votar novamente em uma dúvida"""
        usuario = CustomUser.objects.first()
        duvida = Duvida.objects.first()
        url = reverse("duvidas-votar", args=[duvida.pk])

        self.assertEqual(duvida.votos, 0)

        response = self.client.post(
            url, HTTP_AUTHORIZATION=f"Token {usuario.auth_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        duvida.refresh_from_db()
        self.assertEqual(duvida.votos, 1)

        response = self.client.post(
            url, HTTP_AUTHORIZATION=f"Token {usuario.auth_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        duvida.refresh_from_db()
        self.assertEqual(duvida.votos, 1)

    def test_remover_voto_nao_existente(self):
        """Testa remover um voto que não existe"""
        usuario = CustomUser.objects.first()
        duvida = Duvida.objects.first()
        url = reverse("duvidas-votar", args=[duvida.pk])

        self.assertEqual(duvida.votos, 0)

        response = self.client.delete(
            url, HTTP_AUTHORIZATION=f"Token {usuario.auth_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        duvida.refresh_from_db()
        self.assertEqual(duvida.votos, 0)

    def test_outro_user_deleta_votos_de_outrem(self):
        """Testa se outro usuário que não votou pode remover votos de outrem"""
        usuario = CustomUser.objects.first()
        usuario_intruso = CustomUser.objects.get(pk=2)
        duvida = Duvida.objects.first()
        url = reverse("duvidas-votar", args=[duvida.pk])

        self.assertEqual(duvida.votos, 0)

        response = self.client.post(
            url, HTTP_AUTHORIZATION=f"Token {usuario.auth_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        duvida.refresh_from_db()
        self.assertEqual(duvida.votos, 1)

        response = self.client.delete(
            url, HTTP_AUTHORIZATION=f"Token {usuario_intruso.auth_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        duvida.refresh_from_db()
        self.assertEqual(duvida.votos, 1)
