# Use the official OWASP ModSecurity CRS image as the base
FROM owasp/modsecurity-crs:4.10.0-nginx-202501270601

# Set the working directory to /etc/nginx (avoids long paths)
WORKDIR /etc/nginx

# Copy the template configuration files into the correct locations
COPY ./conf/default.conf templates/conf.d/default.conf.template
COPY ./conf/proxy_frontend.conf templates/includes/proxy_frontend.conf.template
COPY ./conf/proxy_api.conf templates/includes/proxy_api.conf.template
COPY ./conf/proxy_websocket.conf templates/includes/proxy_websocket.conf.template
COPY ./conf/proxy_static_files.conf templates/includes/proxy_static_files.conf.template
COPY ./conf/ssl_settings.conf templates/includes/ssl_settings.conf.template
COPY ./conf/metrics.conf templates/includes/metrics.conf.template

# Default command to start Nginx
CMD ["nginx", "-g", "daemon off;"]