from django.db import models


class Curso(models.Model):
    nome = models.TextField()
    descricao = models.TextField()

    def __str__(self):
        return f"Curso: {self.nome}"


class Disciplinas(models.Model):
    nome = models.TextField()
    descricao = models.TextField()

    cursos = models.ManyToManyField(Curso)

    def __str__(self):
        return f"Curso: {self.nome}"
