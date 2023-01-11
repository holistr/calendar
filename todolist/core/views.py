import requests
from django.contrib.auth import get_user_model, login, logout

from rest_framework import generics, status, permissions
from rest_framework.response import Response

from . import serializers
from .models import User
from .serializers import UpdatePasswordSerializer

USER_MODEL = get_user_model()


class RegistrationView(generics.CreateAPIView):
    model = USER_MODEL
    serializer_class = serializers.RegistrationSerializer


class LoginView(generics.GenericAPIView):
    model = USER_MODEL
    serializer_class = serializers.LoginSerializer

    def post(self, request: requests, *args: str, **kwargs: int) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request=request, user=user)
        return Response(serializer.data)


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.ProfileSerializer
    queryset = USER_MODEL.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> User:
        return self.request.user

    def delete(self, request: requests, *args: str, **kwargs: int) -> Response:
        """Чтобы при выходе из профиля, пользователь не удалялся из БД"""
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdatePasswordView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdatePasswordSerializer

    def get_object(self) -> User:
        return self.request.user
