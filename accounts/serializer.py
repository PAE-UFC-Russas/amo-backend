from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from accounts.models import CustomUser, EmailActivationToken


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = CustomUser(email=validated_data["email"])
        validate_password(validated_data["password"], user=user)
        user.set_password(validated_data["password"])
        user.save()
        return user

    class Meta:
        model = CustomUser
        fields = ["email", "password"]


class EmailValidationTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailActivationToken
        fields = ["token"]
