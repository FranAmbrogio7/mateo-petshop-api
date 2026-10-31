from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginRespuestaSerializer, RegistroSerializer, UsuarioSerializer


class LoginView(ObtainAuthToken):
    """Recibe username y password; devuelve el token y los datos del usuario."""

    @extend_schema(responses=LoginRespuestaSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "usuario": UsuarioSerializer(user).data})


class LogoutView(APIView):
    """Borra el token del usuario: deja de servir en cualquier dispositivo."""

    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={204: None})
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PerfilView(APIView):
    """Datos del usuario logueado (el front lo usa para saber quién es)."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses=UsuarioSerializer)
    def get(self, request):
        return Response(UsuarioSerializer(request.user).data)


class RegistroView(generics.CreateAPIView):
    serializer_class = RegistroSerializer
    permission_classes = [AllowAny]