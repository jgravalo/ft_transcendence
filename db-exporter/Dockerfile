# Step 1: Use a Debian-based image to install necessary tools
FROM debian:stable-slim AS builder

# Install jq and curl
RUN apt-get update && apt-get install -y curl jq

# Step 2: Use the official postgres-exporter image as the final container
FROM prometheuscommunity/postgres-exporter

# Copy only the necessary binaries from the builder stage
COPY --from=builder /usr/bin/curl /usr/bin/jq /usr/bin/

# Copy the custom entrypoint script
COPY ./tool/entrypoint.sh /app/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]