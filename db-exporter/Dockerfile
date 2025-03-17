# Step 1: Use Debian as the base image (instead of a minimal image)
FROM debian:stable-slim

# Install required tools
RUN apt-get update && apt-get install -y \
    curl jq prometheus-postgres-exporter

# Copy the custom entrypoint script
COPY ./tool/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]