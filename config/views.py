from django.views.generic import TemplateView

from catalogo.models import Especie, Producto, Servicio


class HomeView(TemplateView):
    """Página de bienvenida de la API."""

    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_productos"] = Producto.objects.filter(activo=True).count()
        context["total_servicios"] = Servicio.objects.filter(activo=True).count()
        context["total_especies"] = Especie.objects.count()
        return context