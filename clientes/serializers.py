from django.utils import timezone
from rest_framework import serializers

from catalogo.serializers import EspecieSerializer, ServicioSerializer

from .models import Mascota, Turno


class MascotaSerializer(serializers.ModelSerializer):
    """Detalle y escritura: la especie se maneja como ID."""

    class Meta:
        model = Mascota
        fields = ["id", "nombre", "especie", "raza", "fecha_nacimiento", "peso_kg", "observaciones"]


class MascotaListSerializer(MascotaSerializer):
    """Listado: la especie se muestra anidada."""

    especie = EspecieSerializer(read_only=True)


TURNO_FIELDS = ["id", "mascota", "servicio", "fecha_hora", "estado", "notas", "creado"]


class TurnoSerializer(serializers.ModelSerializer):
    """Detalle y escritura: mascota y servicio como IDs, con validaciones."""

    class Meta:
        model = Turno
        fields = TURNO_FIELDS
        read_only_fields = ["estado", "creado"]  # el estado se cambia con una acción (paso 9)

    def validate_mascota(self, mascota):
        user = self.context["request"].user
        if not user.is_staff and mascota.cliente.usuario_id != user.id:
            raise serializers.ValidationError("La mascota no pertenece a tu cuenta.")
        return mascota

    def validate_fecha_hora(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("El turno debe ser en una fecha futura.")
        return value

    def validate(self, data):
        mascota = data.get("mascota", getattr(self.instance, "mascota", None))
        servicio = data.get("servicio", getattr(self.instance, "servicio", None))
        if mascota and servicio and not servicio.especies.filter(pk=mascota.especie_id).exists():
            raise serializers.ValidationError(
                {"servicio": f"{servicio} no está disponible para {mascota.especie}."}
            )
        return data


class TurnoListSerializer(serializers.ModelSerializer):
    """Listado: mascota y servicio anidados."""

    mascota = MascotaListSerializer(read_only=True)
    servicio = ServicioSerializer(read_only=True)

    class Meta:
        model = Turno
        fields = TURNO_FIELDS