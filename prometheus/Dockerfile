# Using the official Prometheus base image
FROM prom/prometheus:v2.42.0

# Copy your custom configuration file
COPY ./conf/prometheus.yml /etc/prometheus/
COPY ./tool/entrypoint.sh /etc/prometheus/

ENTRYPOINT [ "/bin/sh", "/etc/prometheus/entrypoint.sh" ]