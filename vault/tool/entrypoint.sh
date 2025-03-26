#!/usr/bin/env sh

set -ex

# Start Vault in the background
vault server -config=/vault/config/config.hcl &
VAULT_PID=$!

# Wait until Vault is ready
echo "Waiting for Vault to start..."
until vault status | grep -q 'Initialized'; do
    sleep 10
done

# Keep Vault running in the foreground
wait "$VAULT_PID"