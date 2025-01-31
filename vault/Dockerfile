# Usar una imagen oficial de Python como base
FROM hashicorp/vault:latest

RUN apk update
RUN apk add bash

EXPOSE 8200

# Run Vault in dev mode
CMD ["vault", "server", "-dev"]