FROM postgres:15.10-alpine3.20

# Add curl and Vault CLI to interact with HashiCorp Vault
RUN apk add --no-cache curl jq

# Create a non-root user (required to run postgres)
RUN addgroup -S postgresgroup && adduser -S postgresuser -G postgresgroup

# Change ownership of postgres files and switch user
RUN chown -R postgresuser:postgresgroup /var/lib/postgresql
USER postgresuser

# Set the necessary environment variables
ENV POSTGRES_DB=postgres
ENV POSTGRES_USER=postgres

# Set the working directory
WORKDIR /home/postgresuser

# Copy entrypoint script
COPY ./tool/entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh

EXPOSE 5432

#Docker internal volume creation (resets when cleaned)
VOLUME ["/var/lib/postgresql/data"]

ENTRYPOINT ["entrypoint.sh"]