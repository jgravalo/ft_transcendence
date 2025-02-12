#!/usr/bin/env sh

#Exits if an error is encountered + print commands before executing
set -ex

#start vault in background
vault server -config=/vault/config/config.hcl &
VAULT_PID=$!

sleep 5

#Unseal the vault using pre-generated unseal key
vault operator unseal $(grep 'Key 1:' /vault/data/.keys | awk '{print $NF}')

#Put back vault server in foreground
wait "$VAULT_PID"