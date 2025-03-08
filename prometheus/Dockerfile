# Use Alpine to ensure `wget` and SSL work correctly
FROM alpine:latest

# Install necessary tools
RUN apk add --no-cache prometheus wget curl jq envsubst ca-certificates

# Copy Prometheus config and entrypoint
COPY ./conf/prometheus.yml /etc/prometheus/
COPY ./tool/entrypoint.sh /etc/prometheus/

ENTRYPOINT [ "/bin/sh", "/etc/prometheus/entrypoint.sh" ]