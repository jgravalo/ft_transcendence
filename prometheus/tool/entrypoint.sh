#!/bin/sh

set -ex

# Vault URLs
VAULT_AUTH_URL="$VAULT_ADDR/v1/auth/approle/login"

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
# 3) Export the Vault Token
# ---------------------------------------------------------------

export VAULT_TOKEN
envsubst < /etc/prometheus/prometheus.yml > /etc/prometheus/prometheus_resolved.yml
cat /etc/prometheus/prometheus_resolved.yml  # Debugging: Check if the token is replaced

echo "Vault Token exported:  $VAULT_TOKEN. Starting Prometheus..."
exec prometheus --config.file=/etc/prometheus/prometheus_resolved.yml