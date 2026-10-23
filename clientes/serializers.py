from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import serializers

from catalogo.serializers import EspecieSerializer, ServicioSerializer

from .models import Mascota, Turno

User = get_user_model()


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


class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    telefono = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name", "telefono"]
        extra_kwargs = {"email": {"required": True}}

    def validate(self, data):
        # valida la contraseña con las reglas de AUTH_PASSWORD_VALIDATORS de settings
        usuario = User(username=data.get("username"), email=data.get("email"))
        try:
            validate_password(data["password"], usuario)
        except DjangoValidationError as error:
            raise serializers.ValidationError({"password": list(error.messages)})
        return data

    def create(self, validated_data):
        telefono = validated_data.pop("telefono", "")
        user = User.objects.create_user(**validated_data)  # la señal crea el Cliente
        user.cliente.telefono = telefono
        user.cliente.save(update_fields=["telefono"])
        return user
        

class UsuarioSerializer(serializers.Serializer):
    """Datos públicos del usuario logueado."""

    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    nombre = serializers.CharField(source="get_full_name")
    es_staff = serializers.BooleanField(source="is_staff")


class LoginRespuestaSerializer(serializers.Serializer):
    token = serializers.CharField()
    usuario = UsuarioSerializer()