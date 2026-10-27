#!/bin/sh
# Arranque del contenedor en producción (Render)
set -e

echo "==> Aplicando migraciones"
python manage.py migrate --noinput

echo "==> Recolectando archivos estáticos"
python manage.py collectstatic --noinput

echo "==> Creando superusuario (si no existe)"
python manage.py createsuperuser --noinput || true

echo "==> Cargando datos de ejemplo"
python manage.py cargar_datos

echo "==> Iniciando Gunicorn"
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 60