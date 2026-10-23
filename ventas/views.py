from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

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