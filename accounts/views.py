from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from accounts.serializer import UserSerializer


class UserViewSet(ViewSet):
    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
