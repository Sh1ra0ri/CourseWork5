from django.contrib.auth import get_user_model
from rest_framework import generics, permissions

from users.serializers import UserRegisterSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]
