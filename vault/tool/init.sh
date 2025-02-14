#!/usr/bin/env sh

set -ex

VAULT_DATA_DIR="/vault/data"
VAULT_KEYS_FILE="${VAULT_DATA_DIR}/.keys"

# Start Vault in the background
vault server -config=/vault/config/config.hcl &
VAULT_PID=$!

# Wait until Vault is ready
echo "Waiting for Vault to start..."
until curl -s http://127.0.0.1:8200/v1/sys/health | grep -q 'initialized'; do
    sleep 2
done

# If Vault is not initialized, initialize it
if [ ! -f "$VAULT_KEYS_FILE" ]; then
    echo "Initializing Vault..."
    vault operator init -key-shares=1 -key-threshold=1 > "$VAULT_KEYS_FILE"
fi

# Unseal Vault using stored key
echo "Unsealing Vault..."
vault operator unseal $(grep 'Key 1:' "$VAULT_KEYS_FILE" | awk '{print $NF}')

# Keep Vault running in the foreground
wait "$VAULT_PID"