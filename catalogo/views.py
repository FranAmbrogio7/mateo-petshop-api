from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from .filters import ProductoFilter

from .models import Categoria, Especie, Marca, Producto, Proveedor, Servicio
from .permissions import EsAdminOSoloLectura
from .serializers import (
    CategoriaSerializer,
    EspecieSerializer,
    MarcaSerializer,
    ProductoListSerializer,
    ProductoSerializer,
    ProveedorSerializer,
    ServicioSerializer,
)


class EspecieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Especie.objects.all()
    serializer_class = EspecieSerializer


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class MarcaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer


class ServicioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Servicio.objects.filter(activo=True).prefetch_related("especies")
    serializer_class = ServicioSerializer
    filterset_fields = ["especies"]
    search_fields = ["nombre"]  


class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.prefetch_related("marcas")
    serializer_class = ProveedorSerializer
    permission_classes = [IsAdminUser]


class ProductoViewSet(viewsets.ModelViewSet):
    permission_classes = [EsAdminOSoloLectura]
    filterset_class = ProductoFilter
    search_fields = ["nombre", "descripcion", "marca__nombre"]
    ordering_fields = ["precio", "nombre", "stock", "creado"]

    def get_queryset(self):
        qs = Producto.objects.select_related("categoria", "marca").prefetch_related("especies")
        if not self.request.user.is_staff:
            qs = qs.filter(activo=True)  # el público no ve productos dados de baja
        return qs

    def get_serializer_class(self):
        if self.action in ("list", "stock_bajo"):
            return ProductoListSerializer
        return ProductoSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter("umbral", int, description="Stock máximo a incluir (por defecto 5)")
        ]
    )
    @action(detail=False, methods=["get"], url_path="stock-bajo", permission_classes=[IsAdminUser])
    def stock_bajo(self, request):
        """Productos con stock menor o igual al umbral, para reponer."""
        try:
            umbral = int(request.query_params.get("umbral", 5))
        except ValueError:
            raise ValidationError({"umbral": "Debe ser un número entero."})
        qs = self.filter_queryset(self.get_queryset().filter(stock__lte=umbral))
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)