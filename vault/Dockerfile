# Usar una imagen oficial de Python como base
FROM hashicorp/vault:latest

RUN apk update
RUN apk add bash

EXPOSE 8200

COPY conf/config.hcl /vault/config/config.hcl
COPY tool/entrypoint.sh /vault/entrypoint.sh

RUN chmod +x /vault/entrypoint.sh

ENTRYPOINT ["/vault/entrypoint.sh"]