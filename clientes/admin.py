from django.contrib import admin

from .models import Cliente, Mascota, Turno


class MascotaInline(admin.TabularInline):
    model = Mascota
    extra = 0


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ["__str__", "telefono", "direccion"]
    search_fields = ["usuario__username", "usuario__first_name", "usuario__last_name", "telefono"]
    inlines = [MascotaInline]


@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "especie", "raza", "cliente"]
    list_filter = ["especie"]
    search_fields = ["nombre", "raza", "cliente__usuario__username"]
    ordering = ["nombre"]


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ["fecha_hora", "mascota", "servicio", "estado"]
    list_filter = ["estado", "servicio", "fecha_hora"]
    search_fields = ["mascota__nombre", "mascota__cliente__usuario__username"]
    date_hierarchy = "fecha_hora"
    ordering = ["-fecha_hora"]
    list_editable = ["estado"]