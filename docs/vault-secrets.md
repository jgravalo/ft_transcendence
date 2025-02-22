# Vault Secrets Guide

## Overview

Vault is used to securely store and manage secrets such as database passwords, API keys, and Django credentials etc. This guide explains how to add new secrets, retrieve them in Python and Bash, and configure roles and policies for new services if required.

## 1. Adding New Secrets to Vault
To add new secrets, you need to log into the Vault container and manually add them. Vault data is saved in out GitHub repository in /vault/data so that passwords remain persistents during all off our projects.

### Step 1: Access the Vault Container
Make sure all containers are running and then enter the vault container.

```sh
make all
make enter SERVICE=vault
```

### Step 2: Authenticate with vault
Check that vault is running and use the root token from /vault/conf/keys.backup to authenticate.

```sh
vault status
vault login <root_token>
```

### Step 3: Add a New Secret
To add a secret to an existing service with exisiting role/policy use the atch function.

```sh
#For the back (django) container
vault kv patch secret/django new_key="new_value"
#for the db (postgres) container
vault kv patch secret/postgres new_key="new_value"
```

You can also see the existing passwords with :
```sh
#For the back (django) container
vault kv get secret/django
#For the db (postgres) container
vault kv get secret/postgres
```

## 2. Configuring Roles and Policies (Only for new services)
If you want a new service to use vault, you need to create a new role, attach a new policy to it, and then generate **role_id** and **secret_id** tokens that will be used in the containers to authenticate with Vault.

### Step 1: Create a New Policy for a Service
Inside the vault container, create a new policy that gives permission to read the secrets available at /secret/data/new_service.

```sh
#Generate the policy file
echo 'path "secret/data/new_service" {
  capabilities = ["read"]
}' > new_policy.hcl

#Register the policy to Vault
vault policy write new_service_policy new_policy.hcl

#Check that the policy is registered successfully
vault policy read new_policy
```

### Step 2: Create the New Role

```sh
#Create the new role and attach the new policy to it
vault write auth/approle/role/new_service token_policies="new_service_policy"


#Register the policy to Vault
vault policy write new_service_policy my_policy.hcl

#Check that the policy is attached to the role (token_policies = ...)
vault read auth/approle/role/new_service
```

### Step 3: Generate the Tokens.
Retrieve and save the ROLE_ID and SECRET_ID tokens. They will need to be used to retrieve passwords.

```sh
#Role ID
vault read auth/approle/role/new_service/role-id

#Secret ID
vault write -f auth/approle/role/new_service/secret-id
```

## 3. Fetching Secrets in Python
In Django (or any Python script) you can use the **hvac** library to retrieve the secret :

```python
import hvac

# This assumes VAULT_ADDR, VAULT_ROLE_ID and VAULT_SECRET_ID are setup in the .env file
VAULT_ADDR = os.getenv('VAULT_ADDR')
ROLE_ID = os.getenv('VAULT_ROLE_ID')
SECRET_ID = os.getenv('VAULT_SECRET_ID')

client = hvac.Client(url=VAULT_ADDR)

def authenticate_with_vault():
    """ Authenticate with Vault using AppRole """
    try:
        response = client.auth.approle.login(
            role_id=ROLE_ID,
            secret_id=SECRET_ID
        )
        client.token = response['auth']['client_token']
    except Exception as e:
        print(f"Vault Authentication Failed: {e}")

def get_vault_secret(path, key):
    """ Fetch a secret from Vault """
    try:
        response = client.secrets.kv.v2.read_secret_version(path=path)
        return response['data']['data'].get(key, None)
    except Exception as e:
        print(f"Error retrieving secret from Vault: {e}")
        return None

#You can then use the get_vault_secret function to get the secret :
password = get_vault_secret('new_service', 'new_secret')
```

## 4. Fetching Secrets in Bash
I used this mainly for entrypoint scripts launched on containers startup. This is very useful to export secrets as environment variables as you can see in the example below. Note that I included debugging steps to help troubleshoot connection isses to Vault.

```sh
# Vault URls (VAULT_ADDR needs to be set in .env file)
VAULT_AUTH_URL="$VAULT_ADDR/v1/auth/approle/login"
VAULT_SECRET_URL="$VAULT_ADDR/v1/secret/data/new_service"

# Prepare JSON payload for authentication (VAULT_ROLE_ID and VAULT_SECRET_ID need to be set in .env file)
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
NEW_PASSWORD=$(echo "$SECRET_RESPONSE" | jq -r '.data.data.new_password')
if [ -z "$NEW_PASSWORD" ] || [ "$NEW_PASSWORD" = "null" ]; then
    echo "Error: Failed to retrieve Django SuperUser password from Vault!"
    echo "Vault Response: $SECRET_RESPONSE"
    exit 1
fi

# ---------------------------------------------------------------
# 4) Export the new secret/password
# ---------------------------------------------------------------
export NEW_PASSWORD
```