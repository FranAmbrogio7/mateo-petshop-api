from django.db import transaction
from rest_framework import serializers

from catalogo.models import Producto

from .models import DetallePedido, Pedido


class DetallePedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = DetallePedido
        fields = ["id", "producto", "producto_nombre", "cantidad", "precio_unitario", "subtotal"]
        read_only_fields = ["precio_unitario"]


class PedidoSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True)

    class Meta:
        model = Pedido
        fields = ["id", "fecha", "estado", "tipo_entrega", "total", "detalles"]
        read_only_fields = ["fecha", "estado", "total"]

    def validate_detalles(self, detalles):
        if not detalles:
            raise serializers.ValidationError("El pedido debe tener al menos un producto.")
        ids = [d["producto"].id for d in detalles]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Hay productos repetidos en el pedido.")
        for d in detalles:
            producto = d["producto"]
            if not producto.activo:
                raise serializers.ValidationError(f"{producto.nombre} no está disponible.")
            if producto.stock < d["cantidad"]:
                raise serializers.ValidationError(
                    f"Stock insuficiente de {producto.nombre} (disponible: {producto.stock})."
                )
        return detalles

    @transaction.atomic
    def create(self, validated_data):
        detalles = validated_data.pop("detalles")
        pedido = Pedido.objects.create(**validated_data)
        for d in detalles:
            # select_for_update bloquea la fila hasta terminar la transacción
            producto = Producto.objects.select_for_update().get(pk=d["producto"].pk)
            if producto.stock < d["cantidad"]:
                raise serializers.ValidationError(
                    {"detalles": f"Stock insuficiente de {producto.nombre}."}
                )
            producto.stock -= d["cantidad"]
            producto.save(update_fields=["stock"])
            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=d["cantidad"],
                precio_unitario=producto.precio,  # precio congelado al momento de la compra
            )
        pedido.recalcular_total()
        return pedido