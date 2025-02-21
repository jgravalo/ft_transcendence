#!/bin/bash

# Salir al encontrar errores
set -e

#function to export Django superuser password if necessary
export_superuser_password(){

    # Vault URls
    VAULT_AUTH_URL="$VAULT_ADDR/v1/auth/approle/login"
    VAULT_SECRET_URL="$VAULT_ADDR/v1/secret/data/django"

    # Prepare JSON payload for authentication
    AUTH_PAYLOAD=$(jq -n --arg role_id "$VAULT_ROLE_ID" --arg secret_id "$VAULT_SECRET_ID" \
    '{role_id: $role_id, secret_id: $secret_id}')
    
    # ---------------------------------------------------------------
    # 1) Retry loop for Vault login
    # ---------------------------------------------------------------
    MAX_ATTEMPTS=5
    ATTEMPT=0
    SLEEP_SECS=3

    until VAULT_RESPONSE=$(curl -fs -X POST \
        -H "Content-Type: application/json" \
        --data "$AUTH_PAYLOAD" \
        "$VAULT_AUTH_URL")
    do
        ATTEMPT=$((ATTEMPT+1))
        if [ $ATTEMPT -gt $MAX_ATTEMPTS ]; then
            echo "Vault login still failing after $MAX_ATTEMPTS attempts."
            exit 1
        fi
        echo "Vault not ready (attempt $ATTEMPT). Retrying in ${SLEEP_SECS}s..."
        sleep $SLEEP_SECS
    done

    # ---------------------------------------------------------------
    # 2) Extract the Vault token
    # ---------------------------------------------------------------
    VAULT_TOKEN=$(echo "$VAULT_RESPONSE" | jq -r '.auth.client_token')
    if [ -z "$VAULT_TOKEN" ] || [ "$VAULT_TOKEN" = "null" ]; then
        echo "Error: Failed to obtain Vault token!"
        echo "Vault Response: $VAULT_RESPONSE"
        exit 1
    fi

    # ---------------------------------------------------------------
    # 3) Fetch the Django password from Vault
    # ---------------------------------------------------------------
    SECRET_RESPONSE=$(curl -s -X GET -H "X-Vault-Token: $VAULT_TOKEN" "$VAULT_SECRET_URL" || true)

    # If curl fails, SECRET_RESPONSE is empty. Check that:
    if [ -z "$SECRET_RESPONSE" ]; then
        echo "Error: Could not get a response from Vault for the secret."
        exit 1
    fi

    # Extract the password from the JSON response
    DJANGO_SUPERUSER_PASSWORD=$(echo "$SECRET_RESPONSE" | jq -r '.data.data.django_superuser_password')
    if [ -z "$DJANGO_SUPERUSER_PASSWORD" ] || [ "$DJANGO_SUPERUSER_PASSWORD" = "null" ]; then
        echo "Error: Failed to retrieve Django SuperUser password from Vault!"
        echo "Vault Response: $SECRET_RESPONSE"
        exit 1
    fi

    # ---------------------------------------------------------------
    # 4) Export the password
    # ---------------------------------------------------------------
    export DJANGO_SUPERUSER_PASSWORD
}

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
    export_superuser_password
    python manage.py createsuperuser --noinput || true
fi

# Arranca Daphne
echo "Iniciando Daphne..."
exec daphne -b 0.0.0.0 -p 8000 app.asgi:application
