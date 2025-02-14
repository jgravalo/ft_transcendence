#!/bin/sh

set -ex

# Vault Configuration
VAULT_ADDR="http://vault:8200"
VAULT_AUTH_URL="$VAULT_ADDR/v1/auth/approle/login"
VAULT_SECRET_URL="$VAULT_ADDR/v1/secret/data/postgres"

ROLE_ID="6d40c02e-0532-b346-f321-f32b6a241d88"
SECRET_ID="878a456d-3888-4059-0e1e-c6ec5f68937b"

# Prepare JSON payload for authentication
AUTH_PAYLOAD=$(jq -n --arg role_id "$ROLE_ID" --arg secret_id "$SECRET_ID" \
    '{role_id: $role_id, secret_id: $secret_id}')

# Authenticate with Vault and fetch the token
VAULT_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
    --data "$AUTH_PAYLOAD" "$VAULT_AUTH_URL")

# Extract the Vault token
VAULT_TOKEN=$(echo "$VAULT_RESPONSE" | jq -r '.auth.client_token')

# Debug: Print full response if token extraction fails
if [ -z "$VAULT_TOKEN" ] || [ "$VAULT_TOKEN" = "null" ]; then
    echo "Error: Failed to obtain Vault token!"
    echo "Vault Response: $VAULT_RESPONSE"
    exit 1
fi

# Fetch the PostgreSQL password from Vault
SECRET_RESPONSE=$(curl -s -X GET -H "X-Vault-Token: $VAULT_TOKEN" "$VAULT_SECRET_URL")

# Extract the password from the JSON response
POSTGRES_PASSWORD=$(echo "$SECRET_RESPONSE" | jq -r '.data.data.db_password')

# Debug: Print full response if password extraction fails
if [ -z "$POSTGRES_PASSWORD" ] || [ "$POSTGRES_PASSWORD" = "null" ]; then
    echo "Error: Failed to retrieve PostgreSQL password from Vault!"
    echo "Vault Response: $SECRET_RESPONSE"
    exit 1
fi

# Export the password for PostgreSQL
export POSTGRES_PASSWORD

# Start PostgreSQL with the retrieved password
exec docker-entrypoint.sh postgres
