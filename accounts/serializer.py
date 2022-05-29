from telnetlib import SE
from accounts.models import CustomUser
from rest_framework.serializers import Serializer, EmailField, CharField


class UserSerializer(Serializer):
    email = EmailField()
    password = CharField(write_only=True)

    def create(self, validated_data):
        user = CustomUser(email=validated_data["email"], is_active=False)
        user.set_password(validated_data["password"])
        user.save()
        return user

    class Meta:
        model = CustomUser
        fields = ["email", "password"]
