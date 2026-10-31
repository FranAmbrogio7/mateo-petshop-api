from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from catalogo.models import Categoria, Especie, Marca, Producto, Proveedor, Servicio
from clientes.models import Cliente, Mascota, Turno


class Command(BaseCommand):
    help = "Carga datos de ejemplo de Mateo Pet Shop. Se puede ejecutar varias veces sin duplicar."

    @transaction.atomic
    def handle(self, *args, **options):
        # Especies
        especies = {
            nombre: Especie.objects.get_or_create(nombre=nombre)[0]
            for nombre in ["Perro", "Gato", "Ave", "Pez", "Roedor"]
        }
        perro, gato = especies["Perro"], especies["Gato"]

        # Categorías
        categorias = {
            nombre: Categoria.objects.get_or_create(nombre=nombre, defaults={"descripcion": desc})[0]
            for nombre, desc in [
                ("Alimentos", "Alimentos balanceados secos y húmedos"),
                ("Accesorios", "Correas, collares, camas y comederos"),
                ("Higiene", "Shampoo, piedras sanitarias y cepillos"),
                ("Juguetes", "Juguetes para perros y gatos"),
            ]
        }

        # Marcas
        marcas = {
            nombre: Marca.objects.get_or_create(nombre=nombre, defaults={"pais": pais})[0]
            for nombre, pais in [
                ("Royal Canin", "Francia"),
                ("Pro Plan", "Argentina"),
                ("Old Prince", "Argentina"),
                ("Vital Can", "Argentina"),
                ("Pawise", "Países Bajos"),
            ]
        }

        # Proveedores
        for razon, cuit, nombres_marcas in [
            ("Distribuidora del Centro SRL", "30-71234567-8", ["Royal Canin", "Pro Plan"]),
            ("Mascotas Córdoba SA", "30-70987654-3", ["Old Prince", "Vital Can", "Pawise"]),
        ]:
            proveedor, _ = Proveedor.objects.get_or_create(
                cuit=cuit, defaults={"razon_social": razon, "telefono": "0358 462-0000"}
            )
            proveedor.marcas.set([marcas[m] for m in nombres_marcas])

        # Productos: nombre, categoría, marca, especies, precio, stock, peso, etapa
        productos = [
            ("Pro Plan Adulto Raza Mediana 15 kg", "Alimentos", "Pro Plan", ["Perro"], 68000, 12, 15, "adulto"),
            ("Royal Canin Medium Puppy 3 kg", "Alimentos", "Royal Canin", ["Perro"], 31000, 8, 3, "cachorro"),
            ("Old Prince Adulto 20 kg", "Alimentos", "Old Prince", ["Perro"], 52000, 4, 20, "adulto"),
            ("Vital Can Senior 7,5 kg", "Alimentos", "Vital Can", ["Perro"], 29500, 2, 7.5, "senior"),
            ("Royal Canin Indoor Gato 1,5 kg", "Alimentos", "Royal Canin", ["Gato"], 19500, 10, 1.5, "adulto"),
            ("Pro Plan Kitten 1 kg", "Alimentos", "Pro Plan", ["Gato"], 14800, 3, 1, "cachorro"),
            ("Old Prince Gato Senior 3 kg", "Alimentos", "Old Prince", ["Gato"], 21000, 6, 3, "senior"),
            ("Correa extensible 5 m", "Accesorios", "Pawise", ["Perro"], 15900, 10, None, "todas"),
            ("Cama acolchada mediana", "Accesorios", "Pawise", ["Perro", "Gato"], 34000, 5, None, "todas"),
            ("Comedero doble de acero", "Accesorios", "Pawise", ["Perro", "Gato"], 9800, 15, None, "todas"),
            ("Rascador torre 80 cm", "Accesorios", "Pawise", ["Gato"], 42000, 1, None, "todas"),
            ("Shampoo neutro 500 ml", "Higiene", "Pawise", ["Perro", "Gato"], 8900, 20, None, "todas"),
            ("Piedras sanitarias 4 kg", "Higiene", "Old Prince", ["Gato"], 6500, 25, 4, "todas"),
            ("Pelota de goma resistente", "Juguetes", "Pawise", ["Perro"], 5200, 30, None, "todas"),
            ("Caña con plumas", "Juguetes", "Pawise", ["Gato"], 4300, 18, None, "todas"),
        ]
        for nombre, cat, marca, esp, precio, stock, peso, etapa in productos:
            producto, _ = Producto.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "categoria": categorias[cat],
                    "marca": marcas[marca],
                    "precio": precio,
                    "stock": stock,
                    "peso_kg": peso,
                    "etapa_vida": etapa,
                },
            )
            producto.especies.set([especies[e] for e in esp])

        # Servicios: nombre, precio, minutos, especies, descripción
        servicios = {}
        for nombre, precio, minutos, esp, desc in [
            ("Baño y secado", 18000, 60, ["Perro", "Gato"], "Baño con shampoo neutro y secado"),
            ("Corte de pelo", 22000, 90, ["Perro"], "Corte de raza o a tijera"),
            ("Corte de uñas", 6000, 15, ["Perro", "Gato"], "Corte y limado de uñas"),
            ("Deslanado", 20000, 60, ["Perro", "Gato"], "Eliminación del pelo muerto"),
        ]:
            servicio, _ = Servicio.objects.get_or_create(
                nombre=nombre,
                defaults={"precio": precio, "duracion_min": minutos, "descripcion": desc},
            )
            servicio.especies.set([especies[e] for e in esp])
            servicios[nombre] = servicio

        # Cliente de prueba con mascotas y un turno
        User = get_user_model()
        if not User.objects.filter(username="cliente_demo").exists():
            user = User.objects.create_user(
                "cliente_demo", "demo@mateopetshop.com", "demo12345",
                first_name="Lucía", last_name="Gómez",
            )
            cliente, _ = Cliente.objects.get_or_create(usuario=user)
            cliente.telefono = "358 555 1234"
            cliente.direccion = "San Martín 123, Río Cuarto"
            cliente.save()
            toby = Mascota.objects.create(
                cliente=cliente, especie=perro, nombre="Toby", raza="Caniche", peso_kg=6
            )
            Mascota.objects.create(cliente=cliente, especie=gato, nombre="Michi", raza="Siamés", peso_kg=4)
            Turno.objects.create(
                mascota=toby,
                servicio=servicios["Baño y secado"],
                # localtime: las 10:00 en hora argentina (TIME_ZONE), no en UTC
                fecha_hora=timezone.localtime(timezone.now() + timedelta(days=3)).replace(
                    hour=10, minute=0, second=0, microsecond=0
                ),
            )

        self.stdout.write(self.style.SUCCESS(
            f"Datos de Mateo Pet Shop cargados: {Producto.objects.count()} productos, "
            f"{Servicio.objects.count()} servicios, {Especie.objects.count()} especies."
        ))