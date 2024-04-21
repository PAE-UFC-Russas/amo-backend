# accounts/tests/test_registration_user.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import EmailActivationToken, CustomUser
import json

class UserRegistrationTest(APITestCase):
    """Testa a criação de conta e a geração do token de confirmação de e-mail."""

    def test_user_registration_and_email_confirmation_token(self):
        email = "newuser@example.com"
        password = "SecurePassword123!"

        response = self.client.post(
            reverse("registrar-list"),  
            data={"email": email, "password": password},
            format="json"
        )


        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = CustomUser.objects.get(email=email)
        self.assertIsNotNone(user)

 
        email_token = EmailActivationToken.objects.filter(user=user).first()
        self.assertIsNotNone(email_token, "Token de confirmação de e-mail não foi gerado.")


        print(f"Token de confirmação gerado: {email_token.token}")


        self.assertIn("auth_token", response.data["data"])
