from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from catalogo import views as catalogo
from clientes.auth_views import LoginView, LogoutView, PerfilView, RegistroView
from clientes import views as clientes
from ventas import views as ventas

router = DefaultRouter()
router.register("especies", catalogo.EspecieViewSet)
router.register("categorias", catalogo.CategoriaViewSet)
router.register("marcas", catalogo.MarcaViewSet)
router.register("servicios", catalogo.ServicioViewSet)
router.register("proveedores", catalogo.ProveedorViewSet)
router.register("productos", catalogo.ProductoViewSet, basename="producto")
router.register("mascotas", clientes.MascotaViewSet, basename="mascota")
router.register("turnos", clientes.TurnoViewSet, basename="turno")
router.register("pedidos", ventas.PedidoViewSet, basename="pedido")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/login/", LoginView.as_view(), name="login"),
    path("api/auth/logout/", LogoutView.as_view(), name="logout"),
    path("api/auth/registro/", RegistroView.as_view(), name="registro"),
    path("api/auth/perfil/", PerfilView.as_view(), name="perfil"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]