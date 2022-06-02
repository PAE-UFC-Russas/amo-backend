from django.db import models


class Curso(models.Model):
    nome = models.TextField()
    descricao = models.TextField()

    def __str__(self):
        return f"Curso: {self.nome}"


class Disciplina(models.Model):
    pass
