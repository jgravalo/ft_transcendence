#!/bin/sh

set -ex

# Vault URLs
VAULT_AUTH_URL="$VAULT_ADDR/v1/auth/approle/login"
VAULT_SECRET_URL="$VAULT_ADDR/v1/secret/data/grafana"

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

# Debug: Print full response if token extraction fails
if [ -z "$VAULT_TOKEN" ] || [ "$VAULT_TOKEN" = "null" ]; then
    echo "Error: Failed to obtain Vault token!"
    echo "Vault Response: $VAULT_RESPONSE"
    exit 1
fi

# ---------------------------------------------------------------
# 3) Fetch the PostgreSQL password from Vault
# ---------------------------------------------------------------
SECRET_RESPONSE=$(curl -fs -X GET -H "X-Vault-Token: $VAULT_TOKEN" "$VAULT_SECRET_URL")

# If curl fails, SECRET_RESPONSE is empty. Check that:
if [ -z "$SECRET_RESPONSE" ]; then
    echo "Error: Could not get a response from Vault for the secret."
    exit 1
fi

GF_SECURITY_ADMIN_PASSWORD=$(echo "$SECRET_RESPONSE" | jq -r '.data.data.gf_password')
if [ -z "$GF_SECURITY_ADMIN_PASSWORD" ] || [ "$DB_PASSWORD" = "null" ]; then
    echo "Error: Failed to retrieve Grafana password from Vault!"
    echo "Vault Response: $SECRET_RESPONSE"
    exit 1
fi

# ---------------------------------------------------------------
# 4) Export grafana admin password
# ---------------------------------------------------------------
export GF_SECURITY_ADMIN_PASSWORD

exec /usr/sbin/grafana-server --homepath=/usr/share/grafana --config=/etc/grafana/grafana.ini