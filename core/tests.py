from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from accounts.models import CustomUser
from core.models import Curso


class CursoTestCase(APITestCase):
    def setUp(self):
        user = CustomUser.objects.create(
            email="test@user.com", password=make_password("password")
        )
        self.token = Token.objects.create(user=user)

    def test_get_list(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        curso = Curso.objects.create(
            nome="Ciência da Computação",
            descricao="Curso de Bacharelado em Ciência da Computação da UFC em Russas",
        )
        response = self.client.get(reverse("cursos-list"))
        self.assertEqual(
            response.data,
            [{"id": curso.id, "nome": curso.nome, "descricao": curso.descricao}],
        )

    def test_no_auth(self):
        response = self.client.get(reverse("cursos-list"))
        self.assertEqual(response.status_code, 401)
