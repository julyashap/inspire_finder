from rest_framework import generics
from rest_framework.permissions import AllowAny
from api_users.permissions import IsCurrentUser
from api_users.serializers import UserSerializer, AnotherUserSerializer
from users.models import User


class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsCurrentUser]


class UserRetrieveAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.request.user != self.get_object():
            self.serializer_class = AnotherUserSerializer
        return super().get_serializer_class()


class UserDestroyAPIView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsCurrentUser]
