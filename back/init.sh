#!/bin/bash

# Salir al encontrar errores
set -e

# Manejar señales de manera más robusta
cleanup() {
    echo "Limpiando y saliendo..."
    exit 0
}

trap cleanup SIGTERM SIGINT SIGQUIT

# Función para esperar a que la base de datos esté lista
wait_for_db() {
    echo "Esperando a que la base de datos esté lista..."
    while ! nc -z db 5432; do
        echo "Intentando conectar a la base de datos..."
        sleep 2
    done
    echo "Base de datos lista!"
}

# Esperar a que la base de datos esté disponible
wait_for_db

# Ejecuta las migraciones
echo "Aplicando migraciones..."
python manage.py makemigrations
python manage.py migrate

# Compila los archivos de traducción (.po>.mo)
python manage.py compilemessages

# Crea un usuario administrador si es necesario (opcional)
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "Creando superusuario..."
    python manage.py createsuperuser --noinput || true
fi

# Arranca Daphne
echo "Iniciando Daphne..."
exec daphne -b 0.0.0.0 -p 8000 app.asgi:application
