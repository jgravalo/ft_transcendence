#!/bin/sh

# Salir al encontrar errores
set -e

# Ejecuta las migraciones
echo "Aplicando migraciones..."
python manage.py makemigrations
python manage.py migrate

# Compila los archivos de traducción (.po>.mo)
python manage.py compilemessages

# Crea un usuario administrador si es necesario (opcional)
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "Creando superusuario..."
    python manage.py createsuperuser --noinput
fi

# Arranca Daphne
echo "Iniciando Daphne..."
daphne -b 0.0.0.0 -p 8000 app.asgi:application
