from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse as rest_reverse
from django.core.exceptions import ValidationError
from django.core import mail

from accounts.serializer import UserSerializer

from .models import CustomUser, EmailActivationToken

PASSWORD = "M@vr8RjZS8LqrjhV"


class UserAuthTest(APITestCase):
    def setUp(self):
        user = CustomUser.objects.create(
            email="test@user.com", password=make_password(PASSWORD)
        )
        token = Token.objects.create(user=user)

    def test_get_user_api_key(self):
        token = Token.objects.get(user__email="test@user.com")
        data = {"username": "test@user.com", "password": PASSWORD}
        response = self.client.post(reverse("obtain-api-token"), data, format="json")
        self.assertEqual(response.data["token"], token.key)


class CustomUserTest(TestCase):
    def test_create_user(self):
        CustomUser.objects.create_user(email="usuario@test.com", password=PASSWORD)

        user = CustomUser.objects.first()
        self.assertEqual(user.email, "usuario@test.com")
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        CustomUser.objects.create_superuser(email="usuario@test.com", password=PASSWORD)

        user = CustomUser.objects.first()
        self.assertEqual(user.email, "usuario@test.com")
        self.assertTrue(user.is_superuser)


class UserRegistration(TestCase):
    def test_user_registration(self):
        response = self.client.post(
            reverse("usuario-list"),
            {"email": "test@user.com", "password": PASSWORD},
            format="json",
        )
        user = CustomUser.objects.first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.email, response.data["email"])
        self.assertFalse(user.is_active)

    def test_easy_password(self):
        with self.assertRaises(ValidationError):
            UserSerializer().create(
                validated_data={"email": "test@user.com", "password": "password"}
            )

    def test_letters_only_password(self):
        with self.assertRaises(ValidationError):
            UserSerializer().create(
                validated_data={"email": "test@user.com", "password": "hgfedcba"}
            )

    def test_numbers_only_password(self):
        with self.assertRaises(ValidationError):
            UserSerializer().create(
                validated_data={"email": "test@user.com", "password": "15798452"}
            )

    def test_send_registration_token(self):
        response = self.client.post(
            reverse("usuario-list"),
            {"email": "test@user.com", "password": PASSWORD},
            format="json",
        )
        user = CustomUser.objects.first()
        token = EmailActivationToken.objects.first()
        self.assertEqual(user.pk, token.user.pk)
        self.assertIn(f"Seu código de ativação: {token.token}", mail.outbox[0].body)
