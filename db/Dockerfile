FROM postgres:15.10-alpine3.20

# Add curl and Vault CLI to interact with HashiCorp Vault
RUN apk add --no-cache curl jq

# Create a non-root user (required to run postgres)
RUN addgroup -S postgresgroup && adduser -S postgresuser -G postgresgroup

# Fix permissions before switching users
RUN mkdir -p /var/lib/postgresql/data \
    && chown -R postgresuser:postgresgroup /var/lib/postgresql/data \
    && chmod 700 /var/lib/postgresql/data

# Copy entrypoint script
COPY ./tool/entrypoint.sh /home/postgresuser/entrypoint.sh

# Grant execution permissions
RUN chmod +x /home/postgresuser/entrypoint.sh

EXPOSE 5432

#Docker internal volume creation (resets when cleaned)
VOLUME ["/var/lib/postgresql/data"]

#Change to postgres user
USER postgresuser

ENTRYPOINT ["/home/postgresuser/entrypoint.sh"]