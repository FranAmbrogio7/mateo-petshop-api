from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from catalogo import views as catalogo
from clientes import views as clientes

router = DefaultRouter()
router.register("especies", catalogo.EspecieViewSet)
router.register("categorias", catalogo.CategoriaViewSet)
router.register("marcas", catalogo.MarcaViewSet)
router.register("servicios", catalogo.ServicioViewSet)
router.register("proveedores", catalogo.ProveedorViewSet)
router.register("productos", catalogo.ProductoViewSet, basename="producto")
router.register("mascotas", clientes.MascotaViewSet, basename="mascota")
router.register("turnos", clientes.TurnoViewSet, basename="turno")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]