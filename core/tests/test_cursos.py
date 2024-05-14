"""Testes de cursos do aplicativo 'core'."""
import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Curso
from core.serializer import CursoSerializer
from accounts.models import CustomUser, EmailActivationToken


class CursoTestCase(APITestCase):
    """Testes relacionados a CursoViewSet."""

    fixtures = ["groups.yaml"]

    def setUp(self):
        self.admin_user = CustomUser.objects.create_user(
            email="superuser@localhost.com",
            password="qwe123456",
            is_email_active=False,
            is_staff=True,
            is_superuser=True,
        )
        EmailActivationToken.objects.create(
            user=self.admin_user, email="superuser@localhost.com", token="000000"
        )
        response = self.client.post(
            "/registrar/confirmar-email/",
            {"token": "000000"},
        )

        form = {"username": "superuser@localhost.com", "password": "qwe123456"}
        response = self.client.post("/usuario/login/", data=form)
        self.user_auth_token = response.json()["token"]

        self.curso = Curso.objects.create(
            nome="Ciência da Computação",
            descricao="Curso de Bacharelado em Ciência da Computação da UFC em Russas",
        )

    def test_get_list(self):
        """Verifica a lista de Cursos"""
        response = self.client.get(
            reverse("cursos-list"),
            HTTP_AUTHORIZATION=f"Token {self.user_auth_token}",
        )
        self.assertEqual(
            json.loads(response.content)["results"], [CursoSerializer(self.curso).data]
        )

    def test_retrieve(self):
        """Verifica a visualização de um Curso"""
        response = self.client.get(
            reverse("cursos-detail", args=[1]),
            HTTP_AUTHORIZATION=f"Token {self.user_auth_token}",
        )
        self.assertEqual(response.data, CursoSerializer(self.curso).data)

    def test_create(self):
        """Verifica a criação de Cursos."""
        response = self.client.post(
            reverse("cursos-list"),
            {"nome": "curso do admin", "descricao": "curso"},
            HTTP_AUTHORIZATION=f"Token {self.user_auth_token}",
        )
        self.assertEqual(Curso.objects.all().count(), 2)
        self.assertEqual(
            CursoSerializer(Curso.objects.get(nome="curso do admin")).data,
            json.loads(response.content),
        )

    def test_delete(self):
        """Verifica a remoção de Curso"""
        with self.subTest("Remover um Curso"):
            response = self.client.delete(
                reverse("cursos-detail", args=[1]),
                HTTP_AUTHORIZATION=f"Token {self.user_auth_token}",
            )
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            self.assertEqual(Curso.objects.all().count(), 0)

        with self.subTest("Remover Curso inexistente"):
            response = self.client.delete(
                reverse("cursos-detail", args=[100]),
                HTTP_AUTHORIZATION=f"Token {self.user_auth_token}",
            )
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
