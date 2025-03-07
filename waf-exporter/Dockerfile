# Step 1: Use Debian as the base image (instead of a minimal image)
FROM nginx/nginx-prometheus-exporter:latest

ENTRYPOINT ["/usr/bin/nginx-prometheus-exporter", "-nginx.scrape-uri=http://waf:8888/stub_status"]