from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Cliente, Mascota, Turno
from .serializers import (
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