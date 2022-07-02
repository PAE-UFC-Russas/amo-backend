import json

from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.models import CustomUser
from core.models import Curso, Disciplinas
from core.serializer import CursoSerializer, DisciplinaResponseSerializer


class CursoTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            email="user@localhost", password=make_password("password")
        )
        self.admin = CustomUser.objects.create_superuser(
            email="superuser@localhost", password=make_password("adminpassword")
        )

        self.token = Token.objects.create(user=self.user)
        self.admin_token = Token.objects.create(user=self.admin)

        self.curso = Curso.objects.create(
            nome="Ciência da Computação",
            descricao="Curso de Bacharelado em Ciência da Computação da UFC em Russas",
        )

    def test_get_list(self):
        """Verifica a lista de Cursos"""
        response = self.client.get(
            reverse("cursos-list"), HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )
        self.assertEqual(response.data, [CursoSerializer(self.curso).data])

    def test_retrieve(self):
        response = self.client.get(
            reverse("cursos-detail", args=[1]),
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )
        self.assertEqual(response.data, CursoSerializer(self.curso).data)

    def test_create(self):
        """Verifica a criação de Cursos."""
        response = self.client.post(
            reverse("cursos-list"),
            {"nome": "curso do admin", "descricao": "curso"},
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
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
                HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
            )
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            self.assertEqual(Curso.objects.all().count(), 0)

        with self.subTest("Remover Curso inexistente"):
            response = self.client.delete(
                reverse("cursos-detail", args=[100]),
                HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
            )
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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
                HTTP_AUTHORIZATION=f"Token {self.token.key}",
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        with self.subTest("Criar Curso"):
            response = self.client.post(
                reverse("cursos-list"),
                {"nome": "curso", "descricao": ""},
                HTTP_AUTHORIZATION=f"Token {self.token.key}",
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest("Editar Curso"):
            response = self.client.patch(
                reverse("cursos-detail", args=[1]),
                {"nome": "editado"},
                HTTP_AUTHORIZATION=f"Token {self.token.key}",
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest("Remover Curso"):
            response = self.client.delete(
                reverse("cursos-detail", args=[1]),
                HTTP_AUTHORIZATION=f"Token {self.token.key}",
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DisciplinaTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(email="user@localhost", password="")
        self.token = Token.objects.create(user=self.user)

        self.admin = CustomUser.objects.create_superuser(
            email="admin@localhost", password=""
        )
        self.admin_token = Token.objects.create(user=self.admin)

        self.curso_cc = Curso.objects.create(
            nome="Ciência da Computação",
            descricao="Curso de Bacharelado em Ciência da Computação da UFC em Russas",
        )
        self.curso_es = Curso.objects.create(
            nome="Engenharia de Software",
            descricao="Curso de Bacharelado em Engenharia de Software da UFC em Russas",
        )

        self.disciplina_req = Disciplinas.objects.create(
            nome="Requisitos de Software",
            descricao="Definição de requisitos de produto, projetos, restrições, fronteiras de um sistema...",
        )
        self.disciplina_req.cursos.add(self.curso_cc)
        self.disciplina_req.save()

        self.disciplina_fup = Disciplinas.objects.create(
            nome="Fundamentos de Programação",
            descricao="Algoritmos, Conceitos Fundamentais de Programação, Exceções, Controles de Fluxo...",
        )
        self.disciplina_fup.cursos.add(self.curso_cc)
        self.disciplina_fup.save()

    def test_create(self):
        """Verifica a criação de novos objetos"""
        self.assertEqual(Disciplinas.objects.all().count(), 2)
        response = self.client.post(
            reverse("disciplinas-list"),
            dict(
                nome="Introdução a Ciência da Computação",
                descricao="Introduzir a ciência da computação utilizando o seu histórico e fundamentos para dar uma "
                "visão geral da área enquanto ciência.",
                cursos=[self.curso_cc.pk],
            ),
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )
        self.assertEqual(Disciplinas.objects.all().count(), 3)
        self.assertEqual(
            DisciplinaResponseSerializer(
                Disciplinas.objects.get(nome="Introdução a Ciência da Computação")
            ).data,
            json.loads(response.content),
        )

    def test_retrieve(self):
        """Verifica a leitura de um Disciplina"""
        response = self.client.get(
            reverse("disciplinas-detail", args=[1]),
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )
        self.assertEqual(
            DisciplinaResponseSerializer(Disciplinas.objects.get(id=1)).data,
            json.loads(response.content),
        )

    def test_relationship(self):
        """Verifica o funcionamento das relações com Curso"""
        disciplina = Disciplinas.objects.get(nome="Requisitos de Software")
        curso = Curso.objects.get(nome="Ciência da Computação")

        self.assertEqual(disciplina.cursos.count(), 1)
        self.assertIn(curso, disciplina.cursos.all())

        disciplina.cursos.remove(curso)
        self.assertEqual(disciplina.cursos.count(), 0)

    def test_list(self):
        """Verifica que a view list retorna todos os objetos"""
        response = self.client.get(
            reverse("disciplinas-list"),
            HTTP_AUTHORIZATION=f"Token {self.token.key}",
        )
        self.assertEqual(
            [
                DisciplinaResponseSerializer(self.disciplina_req).data,
                DisciplinaResponseSerializer(self.disciplina_fup).data,
            ],
            json.loads(response.content),
        )

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
                HTTP_AUTHORIZATION=f"Token {self.token.key}",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.subTest("Ler Disciplina"):
            response = self.client.get(
                reverse("disciplinas-detail", args=[1]),
                HTTP_AUTHORIZATION=f"Token {self.token.key}",
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        with self.subTest("Criar Disciplina"):
            response = self.client.post(
                reverse("disciplinas-list"),
                {"nome": "disciplina", "descricao": ""},
                HTTP_AUTHORIZATION=f"Token {self.token.key}",
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
