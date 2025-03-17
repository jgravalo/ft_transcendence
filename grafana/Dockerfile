# Use Alpine to ensure `wget` and SSL work correctly
FROM alpine:latest

# Install necessary tools
RUN apk add --no-cache grafana wget curl jq

COPY ./conf/grafana.ini ./etc/grafana/
COPY ./tool/entrypoint.sh ./etc/grafana/

ENTRYPOINT [ "/bin/sh", "/etc/grafana/entrypoint.sh" ]