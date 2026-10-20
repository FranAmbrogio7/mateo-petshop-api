from django.contrib import admin

from .models import DetallePedido, Pedido


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1
    autocomplete_fields = ["producto"]


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ["id", "cliente", "fecha", "estado", "tipo_entrega", "total"]
    list_filter = ["estado", "tipo_entrega", "fecha"]
    search_fields = ["id", "cliente__usuario__username"]
    date_hierarchy = "fecha"
    ordering = ["-fecha"]
    readonly_fields = ["total"]
    inlines = [DetallePedidoInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.recalcular_total()