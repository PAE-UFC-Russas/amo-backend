import json

from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from accounts.models import CustomUser
from core.models import Curso, Disciplinas
from core.serializer import DisciplinaResponseSerializer


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


class DisciplinaTestCase(APITestCase):
    def setUp(self):
        user = CustomUser.objects.create(
            email="test@user.com", password=make_password("password")
        )
        self.token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

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
        )
        self.assertEqual(Disciplinas.objects.all().count(), 3)
        self.assertEqual(
            DisciplinaResponseSerializer(
                Disciplinas.objects.get(nome="Introdução a Ciência da Computação")
            ).data,
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
        response = self.client.get(reverse("disciplinas-list"))
        self.assertEqual(
            [
                DisciplinaResponseSerializer(self.disciplina_req).data,
                DisciplinaResponseSerializer(self.disciplina_fup).data,
            ],
            json.loads(response.content),
        )
