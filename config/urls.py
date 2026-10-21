from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from catalogo import views as catalogo

router = DefaultRouter()
router.register("especies", catalogo.EspecieViewSet)
router.register("categorias", catalogo.CategoriaViewSet)
router.register("marcas", catalogo.MarcaViewSet)
router.register("servicios", catalogo.ServicioViewSet)
router.register("proveedores", catalogo.ProveedorViewSet)
router.register("productos", catalogo.ProductoViewSet, basename="producto")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]