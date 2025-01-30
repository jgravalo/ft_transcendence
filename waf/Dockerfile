# Usa la imagen oficial de Nginx como base
FROM owasp/modsecurity-crs:4.10.0-nginx-202501270601

# Copia el template del fichero de configuration para el "block" principal
COPY ./conf/default.conf.template /etc/nginx/templates/conf.d/default.conf.template
COPY ./conf/proxy_backend.conf.template /etc/nginx/templates/includes/proxy_backend.conf.template

#COPY ./conf/modsecurity.conf.template /etc/nginx/templates/conf.d/modsecurity.conf.template

#Copia los cerificatos para el ssl
COPY ./certs/nginx.crt /etc/nginx/conf/server.crt
COPY ./certs/nginx.key /etc/nginx/conf/server.key

# Expone el puerto 80/443 para el tráfico HTTP/HTTPS
EXPOSE 80
EXPOSE 4

# Comando por defecto para iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]
# CMD ["sh", "docker-entrypoint.sh"]