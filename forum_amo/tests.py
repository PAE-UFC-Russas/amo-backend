"""
TESTS forum_app
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from forum_amo.models import Duvida
from django.contrib.auth.models import AnonymousUser, User
from accounts.models import CustomUser
from forum_amo.serializers import DuvidaSerializer

class DuvidaTestes(APITestCase):
    def set_up(self):
        self.user = CustomUser.objects.create(email='johndoe@localhostt.com', password='password123')
        
        self.admin = CustomUser.objects.create_superuser(email='superjohndoe@localhost.com', password='superpassword123')
            
        self.duvida = Duvida.objects.create(titulo='Distribuição Exponencial', descricao='Probabilidade e Estatística')

    def listar_duvidas(self):
        response = self.client.get(reverse('duvida-list'),
                                   HTTP_AUTHORIZATION = f"Token {self.user.auth_token.key}",) 
        self.assertEqual(response.data, [DuvidaSerializer(self.duvida).data])
