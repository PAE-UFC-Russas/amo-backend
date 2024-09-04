"""Testes de disciplinas do aplicativo 'core'."""
import json

from django.urls import reverse
from rest_framework.test import APITestCase

from accounts.models import CustomUser, EmailActivationToken
from core.models import Curso, Disciplinas
from core.serializer import DisciplinaSerializer


class DisciplinaTestCase(APITestCase):  # pylint: disable=R0902
    """Testes relacionados a DisciplinaViewSet."""

    fixtures = ["groups.yaml"]

    def setUp(self):
        # Criação do Admin
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
        self.admin_auth_token = response.json()["token"]

        # Criação do User
        self.admin_user = CustomUser.objects.create_user(
            email="user@localhost.com",
            password="qwe123456",
            is_email_active=False,
        )
        EmailActivationToken.objects.create(
            user=self.admin_user, email="user@localhost.com", token="000001"
        )
        response = self.client.post(
            "/registrar/confirmar-email/",
            {"token": "000001"},
        )

        form = {"username": "user@localhost.com", "password": "qwe123456"}
        response = self.client.post("/usuario/login/", data=form)
        self.user_auth_token = response.json()["token"]

        #############################################
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
            descricao="Definição de requisitos de produto, projetos, restrições...",
        )
        self.disciplina_req.cursos.add(self.curso_cc)
        self.disciplina_req.save()

        self.disciplina_fup = Disciplinas.objects.create(
            nome="Fundamentos de Programação",
            descricao="Algoritmos, Conceitos Fundamentais de Programação, Exceções...",
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
                descricao="Introduzir a ciência da computação utilizando o seu histórico...",
                cursos=[self.curso_cc.pk],
            ),
            HTTP_AUTHORIZATION=f"Token {self.admin_auth_token}",
        )
        self.assertEqual(Disciplinas.objects.all().count(), 3)
        self.assertEqual(
            DisciplinaSerializer(
                Disciplinas.objects.get(nome="Introdução a Ciência da Computação")
            ).data,
            json.loads(response.content),
        )

    def test_retrieve(self):
        """Verifica a leitura de um Disciplina"""
        response = self.client.get(
            reverse("disciplinas-detail", args=[1]),
            HTTP_AUTHORIZATION=f"Token {self.admin_auth_token}",
        )
        self.assertEqual(
            DisciplinaSerializer(Disciplinas.objects.get(id=1)).data,
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
        """Verifica que a view list retorna objetos esperados"""

        with self.subTest("Todos as disciplinas"):
            response = self.client.get(
                reverse("disciplinas-list"),
                HTTP_AUTHORIZATION=f"Token {self.user_auth_token}",
            )
            self.assertEqual(
                [
                    DisciplinaSerializer(self.disciplina_req).data,
                    DisciplinaSerializer(self.disciplina_fup).data,
                ],
                json.loads(response.content)["results"],
            )

        with self.subTest("Filtragem por curso"):
            response = self.client.get(
                reverse("disciplinas-list"),
                HTTP_AUTHORIZATION=f"Token {self.user_auth_token}",
            )
            self.assertEqual(
                DisciplinaSerializer(
                    Disciplinas.objects.filter(cursos__pk=1), many=True
                ).data,
                json.loads(response.content)["results"],
            )
