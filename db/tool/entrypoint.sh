#!/bin/sh
set -e

# Vault server address (Modify this if necessary)
VAULT_ADDR="http://vault:8200"

# Fetch the password from Vault
export POSTGRES_PASSWORD=$(curl -s --header "X-Vault-Token: $VAULT_TOKEN" \
    $VAULT_ADDR/v1/secret/data/postgres | jq -r '.data.data.password')

if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "Failed to retrieve PostgreSQL password from Vault!"
    exit 1
fi

# Start PostgreSQL with the retrieved password
exec docker-entrypoint.sh postgres