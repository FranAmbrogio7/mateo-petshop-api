from django.contrib import admin

from .models import Categoria, Especie, Marca, Producto, Proveedor, Servicio

admin.site.site_header = "Mateo Pet Shop — Administración"
admin.site.site_title = "Mateo Pet Shop"
admin.site.index_title = "Panel de gestión"


@admin.register(Especie)
class EspecieAdmin(admin.ModelAdmin):
    search_fields = ["nombre"]


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "descripcion"]
    search_fields = ["nombre"]


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "pais"]
    list_filter = ["pais"]
    search_fields = ["nombre"]


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ["razon_social", "cuit", "telefono", "email"]
    search_fields = ["razon_social", "cuit"]
    filter_horizontal = ["marcas"]


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "categoria", "marca", "precio", "stock", "activo"]
    list_filter = ["categoria", "marca", "especies", "etapa_vida", "activo"]
    search_fields = ["nombre", "descripcion", "marca__nombre"]
    ordering = ["nombre"]
    list_editable = ["precio", "stock", "activo"]
    filter_horizontal = ["especies"]
    list_per_page = 25


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ["nombre", "precio", "duracion_min", "activo"]
    list_filter = ["especies", "activo"]
    search_fields = ["nombre"]
    filter_horizontal = ["especies"]