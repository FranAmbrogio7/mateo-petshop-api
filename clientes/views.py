from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Cliente, Mascota, Turno
from .serializers import (
    CambiarEstadoTurnoSerializer,
    MascotaListSerializer,
    MascotaSerializer,
    TurnoListSerializer,
    TurnoSerializer,
)


class MascotaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ["especie"]
    search_fields = ["nombre", "raza"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):  # al generar la documentación
            return Mascota.objects.none()
        qs = Mascota.objects.select_related("especie", "cliente__usuario")
        if self.request.user.is_staff:
            return qs
        return qs.filter(cliente__usuario=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return MascotaListSerializer
        return MascotaSerializer

    def perform_create(self, serializer):
        # get_or_create cubre usuarios creados antes de la señal (no tienen Cliente)
        cliente, _ = Cliente.objects.get_or_create(usuario=self.request.user)
        serializer.save(cliente=cliente)


class TurnoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ["estado", "servicio", "mascota"]
    ordering_fields = ["fecha_hora"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):  # al generar la documentación
            return Turno.objects.none()
        qs = Turno.objects.select_related("mascota__especie", "servicio").prefetch_related(
            "servicio__especies"
        )
        if self.request.user.is_staff:
            return qs
        return qs.filter(mascota__cliente__usuario=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return TurnoListSerializer
        return TurnoSerializer

    @extend_schema(request=CambiarEstadoTurnoSerializer, responses=TurnoSerializer)
    @action(detail=True, methods=["post"], url_path="cambiar-estado")
    def cambiar_estado(self, request, pk=None):
        """El staff puede pasar el turno a cualquier estado; el cliente solo puede cancelarlo."""
        turno = self.get_object()
        entrada = CambiarEstadoTurnoSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        nuevo = entrada.validated_data["estado"]

        if not request.user.is_staff and nuevo != Turno.Estado.CANCELADO:
            return Response(
                {"detail": "Solo podés cancelar tus turnos."}, status=status.HTTP_403_FORBIDDEN
            )
        if turno.estado in (Turno.Estado.REALIZADO, Turno.Estado.CANCELADO):
            return Response(
                {"detail": f"El turno ya está {turno.get_estado_display().lower()}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        turno.estado = nuevo
        turno.save(update_fields=["estado"])
        return Response(TurnoSerializer(turno, context={"request": request}).data)