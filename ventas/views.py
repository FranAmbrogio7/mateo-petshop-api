from django.db import transaction
from django.db.models import F
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from catalogo.models import Producto
from clientes.models import Cliente

from .models import Pedido
from .serializers import PedidoSerializer


class PedidoViewSet(viewsets.ModelViewSet):
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]  # un pedido no se edita: se cancela
    filterset_fields = ["estado", "tipo_entrega"]
    ordering_fields = ["fecha", "total"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):  # al generar la documentación
            return Pedido.objects.none()
        qs = Pedido.objects.select_related("cliente__usuario").prefetch_related("detalles__producto")
        if self.request.user.is_staff:
            return qs
        return qs.filter(cliente__usuario=self.request.user)

    def perform_create(self, serializer):
        cliente, _ = Cliente.objects.get_or_create(usuario=self.request.user)
        serializer.save(cliente=cliente)

    @extend_schema(request=None, responses=PedidoSerializer)
    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        """Cancela un pedido pendiente o pagado y devuelve el stock de sus productos."""
        pedido = self.get_object()
        if pedido.estado not in (Pedido.Estado.PENDIENTE, Pedido.Estado.PAGADO):
            return Response(
                {"detail": f"No se puede cancelar un pedido {pedido.get_estado_display().lower()}."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        with transaction.atomic():
            for detalle in pedido.detalles.all():
                Producto.objects.filter(pk=detalle.producto_id).update(
                    stock=F("stock") + detalle.cantidad
                )
            pedido.estado = Pedido.Estado.CANCELADO
            pedido.save(update_fields=["estado"])
        return Response(self.get_serializer(pedido).data)