# Using the official Prometheus base image
FROM prom/prometheus:v2.42.0

# Copy your custom configuration file
COPY ./conf/prometheus.yml /etc/prometheus/

# No CMD/ENTRYPOINT needed here because the official base image sets it already.
