from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegistroSerializer


def datos_usuario(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "nombre": user.get_full_name(),
        "es_staff": user.is_staff,
    }


class LoginView(ObtainAuthToken):
    """Recibe username y password; devuelve el token y los datos del usuario."""

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "usuario": datos_usuario(user)})


class LogoutView(APIView):
    """Borra el token del usuario: deja de servir en cualquier dispositivo."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PerfilView(APIView):
    """Datos del usuario logueado (el front lo usa para saber quién es)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(datos_usuario(request.user))


class RegistroView(generics.CreateAPIView):
    serializer_class = RegistroSerializer
    permission_classes = [AllowAny]