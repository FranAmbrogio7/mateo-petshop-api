# Mateo Pet Shop — API

API REST de **Mateo Pet Shop**, tienda de alimentos balanceados, accesorios y servicios de estética para mascotas de Río Cuarto. Expone el catálogo de productos, la gestión de mascotas de cada cliente, la reserva de turnos de estética y los pedidos con control de stock.

![Página de bienvenida](docs/capturas/home.png)

## Objetivo

Centralizar la operación del pet shop: catálogo con stock, clientes y sus mascotas, turnos de servicios y pedidos. La API es consumida por el frontend en Next.js desarrollado para Programación III.

## Demo online

| | URL |
| --- | --- |
| Bienvenida | https://mateo-petshop-api.onrender.com/ |
| API navegable | https://mateo-petshop-api.onrender.com/api/ |
| Swagger | https://mateo-petshop-api.onrender.com/api/docs/ |
| Redoc | https://mateo-petshop-api.onrender.com/api/redoc/ |
| Esquema OpenAPI | https://mateo-petshop-api.onrender.com/api/schema/ |
| Administración | https://mateo-petshop-api.onrender.com/admin/ |
| Frontend (repositorio) | https://github.com/FranAmbrogio7/mateo-petshop-web |

> El plan gratuito de Render suspende el servicio después de 15 minutos sin uso. La primera visita puede tardar cerca de un minuto en responder.

**Usuario de prueba:** `cliente_demo` / `demo12345` (tiene dos mascotas y un turno cargados).

## Tecnologías

| Herramienta | Uso |
| --- | --- |
| Python 3.12 + Django 6.1 | framework web, ORM, admin y templates |
| Django REST Framework 3.18 | API REST: serializers, ViewSets, permisos y paginación |
| django-filter | filtros por parámetros de la URL |
| drf-spectacular | esquema OpenAPI, Swagger y Redoc |
| django-cors-headers | CORS para el frontend |
| PostgreSQL | base de datos en Docker y en producción |
| uv | entorno virtual y dependencias con versiones fijas |
| Docker y Docker Compose | contenedores para desarrollo y producción |
| Gunicorn + WhiteNoise | servidor y archivos estáticos en producción |
| Render | despliegue de la API y la base de datos |

## Planificación de la base de datos

La planificación se hizo antes de escribir código ([PR #1](https://github.com/FranAmbrogio7/mateo-petshop-api/pull/1)).

### Entidades

| Modelo | App | Descripción |
| --- | --- | --- |
| Especie | catalogo | Perro, gato, ave, pez, etc. |
| Categoria | catalogo | Alimentos, accesorios, higiene, juguetes |
| Marca | catalogo | Fabricante del producto |
| Proveedor | catalogo | Distribuidor; trabaja varias marcas |
| Producto | catalogo | Artículo a la venta, con precio y stock |
| Servicio | catalogo | Baño, corte, deslanado; con precio y duración |
| Cliente | clientes | Perfil del usuario (teléfono, dirección) |
| Mascota | clientes | Animal de un cliente |
| Turno | clientes | Reserva de un servicio para una mascota |
| Pedido | ventas | Compra de un cliente |
| DetallePedido | ventas | Línea de un pedido (producto, cantidad, precio) |

### Diagrama entidad-relación

```mermaid
erDiagram
    USER ||--|| CLIENTE : tiene
    CLIENTE ||--o{ MASCOTA : "es dueño de"
    CLIENTE ||--o{ PEDIDO : realiza
    ESPECIE ||--o{ MASCOTA : clasifica
    ESPECIE }o--o{ PRODUCTO : "apto para"
    ESPECIE }o--o{ SERVICIO : "aplica a"
    CATEGORIA ||--o{ PRODUCTO : agrupa
    MARCA ||--o{ PRODUCTO : fabrica
    PROVEEDOR }o--o{ MARCA : distribuye
    PEDIDO ||--|{ DETALLE_PEDIDO : contiene
    PRODUCTO ||--o{ DETALLE_PEDIDO : "figura en"
    MASCOTA ||--o{ TURNO : tiene
    SERVICIO ||--o{ TURNO : "se reserva en"
```

### Decisiones de diseño

- `DetallePedido.precio_unitario` guarda el precio al momento de la compra, para que un pedido viejo no cambie si sube el producto.
- `Cliente` es un perfil uno a uno con el `User` de Django; una señal `post_save` lo crea automáticamente al registrar un usuario.
- Productos y servicios se relacionan con `Especie` (muchos a muchos) para filtrar, por ejemplo, "alimento para gatos", y para validar que un servicio aplique a la mascota.
- `PROTECT` donde borrar dejaría datos huérfanos importantes (una marca con productos, un producto ya vendido) y `CASCADE` donde el hijo no tiene sentido sin el padre (las mascotas de un cliente, los detalles de un pedido).
- Un turno no puede repetirse para la misma mascota y horario, salvo que el anterior esté cancelado (restricción condicional en la base de datos).

## API

### Endpoints

| Recurso | Ruta | Métodos | Acceso |
| --- | --- | --- | --- |
| Especies | `/api/especies/` | GET | público |
| Categorías | `/api/categorias/` | GET | público |
| Marcas | `/api/marcas/` | GET | público |
| Servicios | `/api/servicios/` | GET | público |
| Proveedores | `/api/proveedores/` | CRUD | solo staff |
| Productos | `/api/productos/` | CRUD | lectura pública, escritura staff |
| Mascotas | `/api/mascotas/` | CRUD | autenticado, solo las propias |
| Turnos | `/api/turnos/` | CRUD | autenticado, solo los propios |
| Pedidos | `/api/pedidos/` | GET, POST | autenticado, solo los propios |
| Registro | `/api/auth/registro/` | POST | público |
| Login | `/api/auth/login/` | POST | público, devuelve el token |
| Perfil | `/api/auth/perfil/` | GET | autenticado |
| Logout | `/api/auth/logout/` | POST | autenticado, invalida el token |

Son **9 ViewSets**. **Producto**, **Mascota** y **Turno** muestran sus relaciones anidadas solo en el listado (`list`) y como IDs en el detalle, mediante `get_serializer_class()`.

### Acciones personalizadas (`@action`)

| Endpoint | Método | Descripción |
| --- | --- | --- |
| `/api/productos/stock-bajo/?umbral=5` | GET | productos para reponer (solo staff), paginado y filtrable |
| `/api/turnos/{id}/cambiar-estado/` | POST | el staff cambia el estado; el cliente solo puede cancelar |
| `/api/pedidos/{id}/cancelar/` | POST | cancela un pedido pendiente o pagado y devuelve el stock |

### Autenticación

La API acepta **token** (para el frontend) y **sesión** (para el admin y la API navegable).

```bash
# 1. Obtener el token
curl -X POST https://mateo-petshop-api.onrender.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "cliente_demo", "password": "demo12345"}'

# 2. Usarlo en cada consulta protegida
curl https://mateo-petshop-api.onrender.com/api/mascotas/ \
  -H "Authorization: Token <token>"
```

### Paginación, filtros y búsqueda

Todos los listados vienen paginados de a 10 (`count`, `next`, `previous`, `results`).

```text
/api/productos/?especie=2&categoria=1&etapa_vida=adulto
/api/productos/?precio_min=10000&precio_max=40000
/api/productos/?search=royal&ordering=-precio&page=2
/api/turnos/?estado=pendiente&ordering=fecha_hora
```

| ViewSet | Filtros | Búsqueda | Orden |
| --- | --- | --- | --- |
| Productos | categoría, marca, especie, etapa de vida, activo, rango de precio | nombre, descripción, marca | precio, nombre, stock, creado |
| Servicios | especies | nombre | — |
| Mascotas | especie | nombre, raza | — |
| Turnos | estado, servicio, mascota | — | fecha y hora |
| Pedidos | estado, tipo de entrega | — | fecha, total |

### Crear un pedido

Un pedido se crea con sus detalles en un solo POST. La API valida el stock, lo descuenta dentro de una transacción y guarda el precio del momento:

```json
{
  "tipo_entrega": "retiro",
  "detalles": [
    { "producto": 1, "cantidad": 2 },
    { "producto": 3, "cantidad": 1 }
  ]
}
```

## Capturas

### Documentación con Swagger

![Swagger](docs/capturas/swagger.png)

### API navegable: listado paginado con datos anidados

![API navegable](docs/capturas/api-productos.png)

### Panel de administración con filtros y búsqueda

![Admin](docs/capturas/admin.png)

## Instalación local

### Requisitos

- [uv](https://docs.astral.sh/uv/) (instala Python 3.12 si hace falta)
- Docker y Docker Compose (opcional, para usar PostgreSQL)

### Con uv (SQLite)

```bash
git clone https://github.com/FranAmbrogio7/mateo-petshop-api.git
cd mateo-petshop-api
uv sync
cp .env.example .env
uv run python manage.py migrate
uv run python manage.py cargar_datos
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

La API queda en http://127.0.0.1:8000/.

### Con Docker (PostgreSQL)

```bash
cp .env.example .env
docker compose up --build
docker compose exec web python manage.py cargar_datos
docker compose exec web python manage.py createsuperuser
```

### Variables de entorno

| Variable | Descripción | Ejemplo |
| --- | --- | --- |
| `SECRET_KEY` | clave secreta de Django | una cadena larga y aleatoria |
| `DEBUG` | modo depuración | `True` en local, `False` en producción |
| `ALLOWED_HOSTS` | dominios aceptados | `localhost,127.0.0.1` |
| `DATABASE_URL` | base de datos; si no está, usa SQLite | `postgres://usuario:clave@host:5432/base` |
| `CORS_ALLOWED_ORIGINS` | orígenes del frontend | `http://localhost:3000` |
| `CSRF_TRUSTED_ORIGINS` | orígenes de confianza para CSRF | `http://localhost:3000` |

### Datos de ejemplo

`uv run python manage.py cargar_datos` carga especies, categorías, marcas, proveedores, 15 productos, 4 servicios y el usuario `cliente_demo`. Se puede ejecutar varias veces sin duplicar datos.

## Despliegue

La API corre en **Render** a partir del `Dockerfile`, con una base PostgreSQL de Render. En cada arranque, `entrypoint.sh` aplica las migraciones, junta los archivos estáticos, crea el superusuario (desde las variables `DJANGO_SUPERUSER_*`) si no existe, carga los datos de ejemplo e inicia Gunicorn.

## Organización del trabajo

Se trabajó con **GitFlow**: `main` para la versión entregable, `develop` para integración y una rama `feature/*` o `fix/*` por etapa, cada una con su Pull Request. Los commits siguen el formato de Conventional Commits (`feat`, `fix`, `docs`, `chore`, `build`).

## Autor

**Francisco Ambrogio** — Tecnicatura Superior en Desarrollo de Software, ITEC Río Cuarto.
Ingeniería de Software · Evaluación Final Integradora 2026.
