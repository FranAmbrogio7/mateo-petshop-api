from django.core.validators import MinValueValidator
from django.db import models


class Especie(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField("descripción", blank=True)

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Marca(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    pais = models.CharField("país", max_length=60, blank=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    razon_social = models.CharField("razón social", max_length=150)
    cuit = models.CharField(max_length=13, unique=True)
    telefono = models.CharField("teléfono", max_length=30, blank=True)
    email = models.EmailField(blank=True)
    marcas = models.ManyToManyField(Marca, related_name="proveedores", blank=True)

    class Meta:
        verbose_name_plural = "proveedores"
        ordering = ["razon_social"]

    def __str__(self):
        return self.razon_social


class Producto(models.Model):
    class EtapaVida(models.TextChoices):
        CACHORRO = "cachorro", "Cachorro"
        ADULTO = "adulto", "Adulto"
        SENIOR = "senior", "Senior"
        TODAS = "todas", "Todas las etapas"

    nombre = models.CharField(max_length=150)
    descripcion = models.TextField("descripción", blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="productos")
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, related_name="productos")
    especies = models.ManyToManyField(Especie, related_name="productos")
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)
    peso_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    etapa_vida = models.CharField(max_length=10, choices=EtapaVida.choices, default=EtapaVida.TODAS)
    imagen_url = models.URLField(blank=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.marca})"


class Servicio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField("descripción", blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    duracion_min = models.PositiveIntegerField("duración (min)")
    especies = models.ManyToManyField(Especie, related_name="servicios")
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre