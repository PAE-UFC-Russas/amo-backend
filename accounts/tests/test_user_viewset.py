"""Testes sobre UserViewSet do aplicativo 'accounts'."""
from datetime import date
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser
from accounts.serializer import UserSerializer
from core.models import Curso

PASSWORD = "M@vr8RjZS8LqrjhV"


class UserViewSetTest(APITestCase):
    """Testes relacionados a UserViewSet"""

    def setUp(self) -> None:
        self.client.post(
            reverse("registrar-list"),
            {"email": "test@user.com", "password": PASSWORD},
            format="json",
        )
        self.user = CustomUser.objects.first()

        Curso.objects.create(
            nome="Ciência da Computação",
            descricao="Curso de Bacharelado em Ciência da Computação da UFC em Russas",
        )

    def test_list(self):
        """Verifica a visualização de uma lista e usuários."""
        response = self.client.get(
            reverse("usuario-list"),
            HTTP_AUTHORIZATION=f"Token {self.user.auth_token.key}",
        )

        self.assertEqual(response.data, [UserSerializer(self.user).data])

    def test_retrieve(self):
        """Verifica a visualização de um usuário"""
        response = self.client.get(
            reverse("usuario-detail", args=[1]),
            HTTP_AUTHORIZATION=f"Token {self.user.auth_token.key}",
        )

        self.assertIn("perfil", response.data)

        perfil = response.data["perfil"]
        self.assertIn("nome_exibicao", perfil)
        self.assertIn("entrada", perfil)
        self.assertIn("curso", perfil)

    def test_update(self):
        """Verifica a atualização do usuario (no perfil)"""

        response = self.client.patch(
            reverse("usuario-detail", args=["eu"]),
            {
                "perfil": {
                    "nome_completo": "Usuário da Silva",
                    "nome_exibicao": "Usuário",
                    "data_nascimento": "2000-12-30",
                    "matricula": "000000",
                    "curso": 1,
                    "entrada": "2022.1",
                }
            },
            format="json",
            HTTP_AUTHORIZATION=f"Token {self.user.auth_token.key}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.perfil.nome_completo, "Usuário da Silva")
        self.assertEqual(self.user.perfil.nome_exibicao, "Usuário")
        self.assertEqual(self.user.perfil.data_nascimento, date(2000, 12, 30))
        self.assertEqual(self.user.perfil.matricula, "000000")
        self.assertEqual(self.user.perfil.curso_id, 1)
        self.assertEqual(self.user.perfil.entrada, "2022.1")
