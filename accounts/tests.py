from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import CustomUser


class UserAuthTest(APITestCase):
    def setUp(self):
        user = CustomUser.objects.create(
            email="test@user.com", password=make_password("password")
        )
        token = Token.objects.create(user=user)

    def test_get_user_api_key(self):
        token = Token.objects.get(user__email="test@user.com")
        data = {"username": "test@user.com", "password": "password"}
        response = self.client.post(reverse("obtain-api-token"), data, format="json")
        self.assertEqual(response.data["token"], token.key)


class CustomUserTest(TestCase):
    def test_create_user(self):
        CustomUser.objects.create_user(email="usuario@test.com", password="password")

        user = CustomUser.objects.first()
        self.assertEqual(user.email, "usuario@test.com")
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        CustomUser.objects.create_superuser(
            email="usuario@test.com", password="password"
        )

        user = CustomUser.objects.first()
        self.assertEqual(user.email, "usuario@test.com")
        self.assertTrue(user.is_superuser)
