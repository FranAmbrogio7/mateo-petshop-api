from django.conf import settings
from django.db import models

from catalogo.models import Especie, Servicio


class Cliente(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cliente"
    )
    telefono = models.CharField("teléfono", max_length=30, blank=True)
    direccion = models.CharField("dirección", max_length=200, blank=True)

    def __str__(self):
        return self.usuario.get_full_name() or self.usuario.username


class Mascota(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="mascotas")
    especie = models.ForeignKey(Especie, on_delete=models.PROTECT, related_name="mascotas")
    nombre = models.CharField(max_length=60)
    raza = models.CharField(max_length=60, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.especie})"


class Turno(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        CONFIRMADO = "confirmado", "Confirmado"
        REALIZADO = "realizado", "Realizado"
        CANCELADO = "cancelado", "Cancelado"

    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name="turnos")
    servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT, related_name="turnos")
    fecha_hora = models.DateTimeField()
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.PENDIENTE)
    notas = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_hora"]
        constraints = [
            # Un turno cancelado libera el horario: solo choca con turnos activos
            models.UniqueConstraint(
                fields=["mascota", "fecha_hora"],
                condition=~models.Q(estado="cancelado"),
                name="turno_unico_por_mascota",
            )
        ]
    def __str__(self):
        return f"{self.servicio} - {self.mascota} ({self.fecha_hora:%d/%m %H:%M})"