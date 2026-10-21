from rest_framework import serializers

from .models import Categoria, Especie, Marca, Producto, Proveedor, Servicio


class EspecieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especie
        fields = ["id", "nombre"]


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "descripcion"]


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = ["id", "nombre", "pais"]


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ["id", "razon_social", "cuit", "telefono", "email", "marcas"]


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ["id", "nombre", "descripcion", "precio", "duracion_min", "especies", "activo"]


PRODUCTO_FIELDS = [
    "id", "nombre", "descripcion", "categoria", "marca", "especies", "precio",
    "stock", "peso_kg", "etapa_vida", "imagen_url", "activo", "creado",
]


class ProductoSerializer(serializers.ModelSerializer):
    """Detalle y escritura: las relaciones se manejan como IDs."""

    class Meta:
        model = Producto
        fields = PRODUCTO_FIELDS
        read_only_fields = ["creado"]


class ProductoListSerializer(serializers.ModelSerializer):
    """Listado: las relaciones se muestran anidadas (NestedSerializers)."""

    categoria = CategoriaSerializer(read_only=True)
    marca = MarcaSerializer(read_only=True)
    especies = EspecieSerializer(many=True, read_only=True)

    class Meta:
        model = Producto
        fields = PRODUCTO_FIELDS