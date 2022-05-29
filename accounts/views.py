from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from accounts.models import CustomUser
from accounts.serializer import UserSerializer


class UserViewSet(ViewSet):
    @extend_schema(request=UserSerializer, responses=UserSerializer)
    def create(self, request):
        """Realiza o cadastro de um novo usuário."""
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
