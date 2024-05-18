"""Testes de controle de acesso no aplicativo 'core'."""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser, EmailActivationToken
from core.models import Curso, Disciplinas

PASSWORD = "M@vr8RjZS8LqrjhV"


class CursoAccessPolicyTestCase(APITestCase):
    """Verifica o controle de acesso para CursoViewSet"""

    fixtures = ["groups.yaml"]

    def setUp(self) -> None:
        self.email = "user@localhost.com"
        self.password = PASSWORD
        self.client.post(
            reverse("registrar-list"),
            {"email": "user@localhost.com", "password": PASSWORD},
            format="json",
        )

        self.user = CustomUser.objects.first()

        activation_token = EmailActivationToken.objects.first()
        response = self.client.post(
            "/registrar/confirmar-email/",
            {"token": f"{activation_token.token}"},
        )

        form = {"username": "user@localhost.com", "password": PASSWORD}
        response = self.client.post("/usuario/login/", data=form)
        self.user_auth_token = response.json()["token"]

        Curso.objects.create(nome="Título", descricao="Descrição")

    def test_unauthenticated_access(self):
        """Verifica acesso de usuários não autenticados."""
        with self.subTest("Listar Cursos"):
            response = self.client.get(reverse("cursos-list"))
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest("Detalhe de Curso"):
            response = self.client.get(reverse("cursos-detail", args=[1]))
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest("Criar Curso"):
            response = self.client.post(
                reverse("cursos-list"), {"nome": "curso", "descricao": ""}
            )
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest("Editar Curso"):
            response = self.client.patch(
                reverse("cursos-detail", args=[1]), {"nome": "editado"}
            )
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest("Remover Curso"):
            response = self.client.delete(reverse("cursos-detail", args=[1]))
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_access(self):
        """Verifica acesso de usuários comuns autenticados."""
        with self.subTest("Ler Curso"):
            response = self.client.get(
                reverse("cursos-detail", args=[1]),
                {"nome": "editado"},
                HTTP_AUTHORIZATION=f"Token {self.user_auth_token}",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        with self.subTest("Criar Curso"):
            response = self.client.post(
                reverse("cursos-list"),
                {"nome": "curso", "descricao": ""},
                HTTP_AUTHORIZATION=f"Token {self.user_auth_token}",
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest("Editar Curso"):
            response = self.client.patch(
                reverse("cursos-detail", args=[1]),
                {"nome": "editado"},
                HTTP_AUTHORIZATION=f"Token {self.user_auth_token}",
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest("Remover Curso"):
            response = self.client.delete(
                reverse("cursos-detail", args=[1]),
                HTTP_AUTHORIZATION=f"Token {self.user_auth_token}",
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DisciplinaAccessPolicyTestCase(APITestCase):
    """Verifica o controle de acesso para DisciplinaViewSet"""

    fixtures = ["groups.yaml"]

    def setUp(self) -> None:
        self.email = "user@localhost.com"
        self.password = PASSWORD
        self.client.post(
            reverse("registrar-list"),
            {"email": "user@localhost.com", "password": PASSWORD},
            format="json",
        )

        self.user = CustomUser.objects.first()

        activation_token = EmailActivationToken.objects.first()
        response = self.client.post(
            "/registrar/confirmar-email/",
            {"token": f"{activation_token.token}"},
        )

        form = {"username": "user@localhost.com", "password": PASSWORD}
        response = self.client.post("/usuario/login/", data=form)
        self.user_auth_token = response.json()["token"]

        Disciplinas.objects.create(nome="Título", descricao="Descrição")

    def test_unauthenticated_access(self):
        """Verifica controle de acesso para usuários não autenticados"""
        with self.subTest("Listar Disciplinas"):
            response = self.client.get(reverse("disciplinas-list"))
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest("Ler Disciplina"):
            response = self.client.get(reverse("disciplinas-detail", args=[1]))
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        with self.subTest("Criar Disciplina"):
            response = self.client.post(
                reverse("disciplinas-list"), {"nome": "disciplina", "descricao": ""}
            )
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_access(self):
        """Verifica controle de acesso para usuários autenticados"""

        with self.subTest("Listar Disciplinas"):
            response = self.client.get(
                reverse("disciplinas-list"),
                HTTP_AUTHORIZATION=f"Token {self.user_auth_token}",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("Ler Disciplina"):
            response = self.client.get(
                reverse("disciplinas-detail", args=[1]),
                HTTP_AUTHORIZATION=f"Token {self.user_auth_token}",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("Criar Disciplina"):
            response = self.client.post(
                reverse("disciplinas-list"),
                {"nome": "disciplina", "descricao": ""},
                HTTP_AUTHORIZATION=f"Token {self.user_auth_token}",
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
